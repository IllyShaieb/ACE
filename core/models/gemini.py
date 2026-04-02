"""core.models.gemini: This module defines the GeminiModel class, which integrates with Google's
Gemini API to provide advanced language processing capabilities for the ACE application.
"""

import os
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import errors, types

from core.adapters.protocols import (
    ConversationStorageAdapterProtocol,
    LogStorageAdapterProtocol,
)
from core.models.base import ThinkingLevel
from core.tools import discover_tools
from core.tools.protocols import ToolProtocol


class GeminiIntelligenceModel:
    """A model powered by the Gemini API that handles complex queries, tool orchestration,
    and automatic fallback to alternate models when the primary is unavailable."""

    _CACHE_DISPLAY_NAME = "ace-system-context"
    _CACHE_TTL = "3600s"
    _MAX_ORCHESTRATION_LOOPS = 5

    def __init__(
        self,
        client: genai.Client,
        storage_adapter: ConversationStorageAdapterProtocol,
        tools: Optional[List[ToolProtocol]] = None,
        services: Optional[Dict[str, Any]] = None,
        model: str = "gemini-2.5-flash-lite",
        fallback_models: Optional[List[str]] = None,
        thinking_level: ThinkingLevel = ThinkingLevel.LOW,
        log_storage_adapter: Optional[LogStorageAdapterProtocol] = None,
    ):
        """Initialise the GeminiIntelligenceModel with any necessary setup.

        Args:
            client (genai.Client): The Gemini API client instance.
            storage_adapter (ConversationStorageAdapterProtocol): Adapter for conversation storage.
            tools (Optional[List[ToolProtocol]]): A list of tools that the model can use
                to enhance its capabilities. If None, it will automatically discover tools.
            services (Optional[Dict[str, Any]]): A dictionary of available services that tools
                might depend on. If None, it will be treated as an empty dictionary.
            model (str): The primary model name to use for the Gemini API client.
            fallback_models (Optional[List[str]]): An ordered list of fallback model names
                to try when the primary model returns an UNAVAILABLE error.
            thinking_level (ThinkingLevel): The level of thinking or reasoning to allow.
            log_storage_adapter (Optional[LogStorageAdapterProtocol]): Adapter for log storage.
        """
        # --- Core dependencies and configuration ---
        self.client = client  # Gemini API client instance
        self.model = model  # Primary model name
        self._models = self._build_model_list(
            model, fallback_models
        )  # Ordered list of models (primary + fallbacks)
        self.thinking_level = thinking_level.value  # Reasoning level (int)

        # --- Storage and logging adapters ---
        self.storage_adapter = storage_adapter  # Conversation storage
        self.log_storage_adapter = log_storage_adapter  # Log storage

        # --- Tool and persona setup ---
        self.tools = (
            tools if tools is not None else discover_tools(services)
        )  # Tool registry

        self._log_event(
            level="INFO",
            source="model",
            message=f"Model initialized with primary model '{self.model}' and thinking level '{thinking_level.name}'.",
            details=f"Available tools: {[tool.name for tool in self.tools]}",
        )

        self.persona = self._load_persona()  # Persona markdown text

        # --- Session and cache state ---
        self.session_id = None  # Current session ID
        self._cache = self._try_create_cache()  # System context cache (if available)
        self._chat_config = (
            self._build_chat_config()
        )  # Chat configuration (with/without cache)

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_model_list(primary: str, fallbacks: Optional[List[str]]) -> List[str]:
        """Return a de-duplicated, ordered list starting with the primary model.

        Args:
            primary (str): The primary model name.
            fallbacks (Optional[List[str]]): Optional fallback model names.

        Returns:
            List[str]: The ordered model list.
        """
        models = [primary]
        if fallbacks:
            models.extend(m for m in fallbacks if m != primary)
        return models

    def _load_persona(self) -> str:
        """Load the persona definition from the data directory.

        Returns:
            str: The raw persona markdown text.
        """
        try:
            persona_path = os.path.join(os.path.dirname(__file__), "../data/PERSONA.md")
            with open(persona_path, "r", encoding="utf-8") as f:
                self._log_event(
                    level="INFO",
                    source="model",
                    message="Loaded persona definition successfully.",
                )
                return f.read()
        except FileNotFoundError as e:
            self._log_event(
                level="ERROR",
                source="model",
                message="Persona definition file not found.",
                details=f"Error: {e}",
            )
            return "You are a helpful assistant designed to answer user queries and perform tasks using available tools when necessary."

    def _build_system_instruction(self) -> types.Content:
        """Build the system instruction Content from the loaded persona.

        Returns:
            types.Content: The system instruction for Gemini.
        """
        return types.Content(
            role="system",
            parts=[types.Part(text=self.persona)],
        )

    def _build_thinking_config(self) -> types.ThinkingConfig:
        """Build the ThinkingConfig based on the configured thinking level.

        Returns:
            types.ThinkingConfig: The thinking configuration for Gemini.
        """
        return types.ThinkingConfig(
            include_thoughts=self.thinking_level > ThinkingLevel.NONE.value,
            thinking_budget=self.thinking_level,
        )

    def _build_gemini_tools(self) -> List[types.Tool]:
        """Wrap the formatted function declarations in a Gemini Tool list.

        Returns:
            List[types.Tool]: Tools ready for use in a Gemini config.
        """
        return [types.Tool(function_declarations=self._format_tools_for_gemini())]

    def _try_create_cache(self) -> Optional[Any]:
        """Attempt to create a server-side context cache for the system instruction and tools.

        Falls back to None when the content is too small to meet the API's minimum token
        threshold, allowing the caller to embed the context directly in every request instead.

        Returns:
            The cache object, or None if creation failed.
        """
        try:
            return self.client.caches.create(
                model=f"models/{self.model}",
                config=types.CreateCachedContentConfig(
                    display_name=self._CACHE_DISPLAY_NAME,
                    system_instruction=self._build_system_instruction(),
                    tools=self._build_gemini_tools(),
                    ttl=self._CACHE_TTL,
                ),
            )
        except errors.ClientError:
            return None

    def _build_chat_config(self) -> types.GenerateContentConfig:
        """Build the chat configuration, referencing the cache when available or embedding
        the system instruction and tools directly as a fallback.

        Returns:
            types.GenerateContentConfig: The configuration for the chat session.
        """
        thinking_config = self._build_thinking_config()

        if self._cache:
            return types.GenerateContentConfig(
                cached_content=self._cache.name,
                thinking_config=thinking_config,
            )

        return types.GenerateContentConfig(
            system_instruction=self._build_system_instruction(),
            thinking_config=thinking_config,
            tools=self._build_gemini_tools(),
        )

    def _build_history(self) -> List[types.Content]:
        """Fetch the session's chat history from the DB and format it for Gemini."""
        if not self.session_id:
            return []

        db_messages = self.storage_adapter.get_session_messages(self.session_id)
        history = []
        for msg in db_messages:
            role = "user" if msg["sender"].lower() == "user" else "model"
            history.append(
                types.Content(role=role, parts=[types.Part(text=msg["content"])])
            )
        return history

    def _create_chat_session(self, model_name: Optional[str] = None) -> Any:
        """Create a fresh Gemini chat session.

        Args:
            model_name (Optional[str]): The model to use. Defaults to the primary model.

        Returns:
            The Gemini chat session object.
        """
        return self.client.chats.create(
            model=model_name or self.model,
            config=self._chat_config,
            history=self._build_history(),
        )

    # ------------------------------------------------------------------
    # Tool formatting
    # ------------------------------------------------------------------

    def _format_tools_for_gemini(self) -> List[types.FunctionDeclaration]:
        """Convert the registered tools into Gemini FunctionDeclaration objects.

        Returns:
            List[types.FunctionDeclaration]: A list of tools formatted for the Gemini API.
        """
        return [
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=types.Schema(
                    type=tool.parameters_schema.get("type", "OBJECT"),
                    properties=tool.parameters_schema.get("properties", {}),
                    required=tool.parameters_schema.get("required", []),
                ),
            )
            for tool in self.tools
        ]

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def load_session(self, session_id: Optional[str] = None) -> None:
        """Loads an existing session or sets up a new one, then builds the chat.

        Args:
            session_id (Optional[str]): The ID of the session to load. If None, a new session will be created on first message.
        """
        self.session_id = session_id
        self.chat = self._create_chat_session()

    def close(self) -> None:
        """Delete the context cache to free up resources.

        Should be called when the model is no longer needed to avoid incurring
        unnecessary cache storage costs.
        """
        if self._cache:
            self.client.caches.delete(name=self._cache.name)
            self._cache = None

    # ------------------------------------------------------------------
    # Query processing (public API)
    # ------------------------------------------------------------------

    def _save_exchange(self, query: str, response: str) -> None:
        """Save the user's query and the model's response to the database.

        Args:
            query (str): The user's input query.
            response (str): The model's generated response.
        """
        if not self.session_id:
            self.session_id = self.storage_adapter.create_session(title="New Chat")

        self.storage_adapter.save_message(self.session_id, role="USER", content=query)
        self.storage_adapter.save_message(
            self.session_id, role="model", content=response
        )

        # Trigger auto-title if this is the very first exchange
        if len(self.storage_adapter.get_session_messages(self.session_id)) <= 2:
            self._auto_title(query)

    def _auto_title(self, first_query: str) -> None:
        """Generate a short title for the session based on the first query.

        Args:
            first_query (str): The initial user query to base the title on.
        """
        try:
            prompt = f"Summarize this query into a short title (3-4 words max). Do not use quotes or punctuation: {first_query}"
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            if response and response.text:
                clean_title = response.text.strip().replace('"', "").replace("'", "")
                self.storage_adapter.update_session_title(self.session_id, clean_title)
        except Exception:
            # Silently fail on titling errors to keep the chat flow smooth
            pass

    async def process_query(self, query: str) -> str:
        """Process a user query, automatically falling back to alternate models on
        UNAVAILABLE errors.

        The first attempt uses the existing chat session to preserve conversation history.
        Fallback attempts create a fresh session with the next model in the list. After any
        failure the session is rebuilt to clear potentially corrupt history.

        Args:
            query (str): The user query to process.

        Returns:
            str: The response generated by the model.
        """
        # Log the incoming query
        self._log_event(
            level="INFO",
            source="model",
            message="Processing user query.",
            details=f"Query length: {len(query)} characters",
        )

        for i, model_name in enumerate(self._models):
            try:
                if i > 0:
                    self._log_event(
                        level="WARNING",
                        source="model",
                        message=f"Model unavailable. Falling back to alternate model.",
                        details=f"Attempting with: {model_name}",
                    )
                    self.chat = self._create_chat_session(model_name)

                response_text = await self._orchestrate(query)
                self._log_event(
                    level="INFO",
                    source="model",
                    message=f"Successfully generated response.",
                    details=f"Model used: {model_name}. Response Length: {len(response_text)} characters",
                )
                self._save_exchange(query, response_text)
                return response_text
            except errors.APIError as e:
                if self._is_retriable(e) and i < len(self._models) - 1:
                    continue

                # Non-retriable or final model: rebuild to clear corrupt history
                self.chat = self._create_chat_session(self._models[0])
                error_message = (
                    f"I'm afraid I encountered an error: {e.status} - {e.message}"
                )
                self._save_exchange(query, error_message)
                self._log_event(
                    level="ERROR",
                    source="model",
                    message=error_message,
                    details=f"Model used: {self._models[i]}",
                )
                return error_message

        # Unreachable unless _models is empty, but guard defensively.
        error_message = "I'm afraid an unexpected error occurred."
        self._save_exchange(query, error_message)
        self._log_event(
            level="ERROR",
            source="model",
            message=error_message,
            details="No models available to process the query.",
        )
        return error_message

    # ------------------------------------------------------------------
    # Query processing (private helpers)
    # ------------------------------------------------------------------

    def _log_event(
        self, level: str, source: str, message: str, details: Optional[str] = None
    ) -> None:
        """Log an event to the log storage adapter.

        Args:
            level (str): The severity level of the event (e.g., "INFO", "ERROR").
            source (str): The source of the event (e.g., "model", "tool").
            message (str): A descriptive message about the event.
            details (Optional[str]): Additional details or context about the event.
        """
        if self.log_storage_adapter:
            self.log_storage_adapter.log_event(
                level=level, source=source, message=message, details=details
            )

    async def _orchestrate(self, query: str) -> str:
        """Run the Intent -> Execution -> Synthesis loop for a single query.

        Args:
            query (str): The user query.

        Returns:
            str: The final text response from the model.
        """
        response = self.chat.send_message(query)
        iterations = 0

        while iterations < self._MAX_ORCHESTRATION_LOOPS:
            candidates = response.candidates or []
            if not candidates or not candidates[0].content:
                break

            parts = candidates[0].content.parts or []
            function_calls = [p.function_call for p in parts if p.function_call]

            if not function_calls:
                break

            # Execute every requested tool and send results back to the model
            function_responses = [self._execute_tool(fc) for fc in function_calls]
            response = self.chat.send_message(function_responses)

            iterations += 1

            if iterations == self._MAX_ORCHESTRATION_LOOPS:
                return "I'm sorry, but I wasn't able to complete your request after multiple attempts."

        return self._extract_text(response)

    def _execute_tool(self, function_call: Any) -> types.Part:
        """Execute a single tool call and wrap the outcome in a FunctionResponse Part.

        Args:
            function_call: The Gemini function-call object containing the tool name and args.

        Returns:
            types.Part: A FunctionResponse part containing either the result or an error.
        """
        tool_name = function_call.name or ""
        tool_args = function_call.args or {}

        self._log_event(
            level="INFO",
            source=f"model:tool:{tool_name}",
            message=f"Executing tool: {tool_name}",
            details=f"Arguments: {tool_args}",
        )

        tool = next((t for t in self.tools if t.name == tool_name), None)

        if tool is None:
            result_data: Dict[str, Any] = {"error": "Requested tool not found."}
            self._log_event(
                level="ERROR",
                source="model",
                message=f"Tool not found: {tool_name}",
                details=f"Available tools: {[t.name for t in self.tools]}",
            )
        else:
            try:
                result_data = {"result": tool.execute(**tool_args)}
                self._log_event(
                    level="INFO",
                    source=f"model:tool:{tool_name}",
                    message=f"Tool executed successfully",
                )
            except Exception as e:
                self._log_event(
                    level="ERROR",
                    source=f"model:tool:{tool_name}",
                    message=f"Error executing tool: {tool_name}",
                    details=f"Error: {str(e)}",
                )
                result_data = {"error": f"Tool execution failed: {str(e)}"}

        return types.Part.from_function_response(
            name=tool_name,
            response=result_data,
        )

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Extract the final text from a Gemini response, filtering out thought parts.

        Args:
            response: The Gemini GenerateContentResponse.

        Returns:
            str: The concatenated text from all non-thought parts.
        """
        candidates = response.candidates or []
        parts = (
            candidates[0].content.parts or []
            if candidates and candidates[0].content
            else []
        )
        return "".join(
            part.text
            for part in parts
            if part.text and getattr(part, "thought", None) is not True
        )

    @staticmethod
    def _is_retriable(error: errors.APIError) -> bool:
        """Determine whether an API error indicates a transient availability issue
        that warrants retrying with a different model.

        Args:
            error (errors.APIError): The error raised by the Gemini API.

        Returns:
            bool: True if the error is retriable, False otherwise.
        """
        return (
            getattr(error, "status", None) == "UNAVAILABLE"
            or getattr(error, "code", None) == 503
        )
