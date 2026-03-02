"""core.models: This module defines the model classes for the ACE application, responsible for managing
data and business logic."""

import os
from enum import Enum
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import errors, types

from core.protocols import ToolProtocol
from core.tools import discover_tools


class ThinkingLevel(Enum):
    """Enum to represent different levels of thinking or reasoning that the model can perform."""

    NONE = 0
    LOW = 1024
    MEDIUM = 2048
    HIGH = 4096


class MinimumViableModel:
    """A simple model implementation that processes user queries and returns responses based on
    basic keyword recognition."""

    async def process_query(self, query: str) -> str:
        """Process a user query and return a response.

        Args:
            query (str): The user query to process.
        """
        cleaned_query = query.strip().lower()

        truth_map = {
            "greeting": (
                any(greet in cleaned_query for greet in ["hello", "hi", "hey"]),
                "Hello! How can I assist you today?",
            ),
            "help": (
                "help" in cleaned_query,
                "Sure! You can ask me anything or type 'exit' to quit.",
            ),
            "meaning of life": (
                "meaning of life" in cleaned_query,
                "42 is the answer to the ultimate question of life, the universe, and everything.",
            ),
        }

        for key, (condition, response) in truth_map.items():
            if condition:
                return response
        return "I'm not sure how to respond to that."


class GeminiIntelligenceModel:
    """A model powered by the Gemini API that handles complex queries, tool orchestration,
    and automatic fallback to alternate models when the primary is unavailable."""

    _CACHE_DISPLAY_NAME = "ace-system-context"
    _CACHE_TTL = "3600s"
    _MAX_ORCHESTRATION_LOOPS = 5

    def __init__(
        self,
        client: genai.Client,
        tools: Optional[List[ToolProtocol]] = None,
        services: Optional[Dict[str, Any]] = None,
        model: str = "gemini-2.5-flash-lite",
        fallback_models: Optional[List[str]] = None,
        thinking_level: ThinkingLevel = ThinkingLevel.LOW,
    ):
        """Initialise the GeminiIntelligenceModel with any necessary setup.

        Args:
            client (genai.Client): The Gemini API client instance.
            tools (Optional[List[ToolProtocol]]): A list of tools that the model can use
                to enhance its capabilities. If None, it will automatically discover tools.
            services (Optional[Dict[str, Any]]): A dictionary of available services that tools
                might depend on. If None, it will be treated as an empty dictionary.
            model (str): The primary model name to use for the Gemini API client.
            fallback_models (Optional[List[str]]): An ordered list of fallback model names
                to try when the primary model returns an UNAVAILABLE error.
            thinking_level (ThinkingLevel): The level of thinking or reasoning to allow.
        """
        self.client = client
        self.model = model
        self._models = self._build_model_list(model, fallback_models)
        self.thinking_level = thinking_level.value
        self.tools = tools if tools is not None else discover_tools(services)
        self.persona = self._load_persona()

        self._cache = self._try_create_cache()
        self._chat_config = self._build_chat_config()
        self.chat = self._create_chat_session()

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

    @staticmethod
    def _load_persona() -> str:
        """Load the persona definition from the data directory.

        Returns:
            str: The raw persona markdown text.
        """
        try:
            persona_path = os.path.join(os.path.dirname(__file__), "../data/PERSONA.md")
            with open(persona_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
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
        for i, model_name in enumerate(self._models):
            try:
                if i > 0:
                    self.chat = self._create_chat_session(model_name)
                return await self._orchestrate(query)
            except errors.APIError as e:
                if self._is_retriable(e) and i < len(self._models) - 1:
                    continue

                # Non-retriable or final model: rebuild to clear corrupt history
                self.chat = self._create_chat_session(self._models[0])
                return f"I'm afraid I encountered an error: {e.status} - {e.message}"

        # Unreachable unless _models is empty, but guard defensively.
        return "I'm afraid an unexpected error occurred."

    # ------------------------------------------------------------------
    # Query processing (private helpers)
    # ------------------------------------------------------------------

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

        tool = next((t for t in self.tools if t.name == tool_name), None)

        if tool is None:
            result_data: Dict[str, Any] = {"error": "Requested tool not found."}
        else:
            try:
                result_data = {"result": tool.execute(**tool_args)}
            except Exception as e:
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
