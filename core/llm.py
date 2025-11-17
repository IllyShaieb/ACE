"""llm.py: Handles all interactions with external LLM APIs.


This module defines the APIService protocol for flexible API switching and

provides an implementation for the Google GenAI service with native tool calling.
"""

import os
import re
from typing import Any, Callable, Dict, List, Optional, Protocol, cast

from google import genai
from google.genai import types

from .actions import ActionHandler


class APIService(Protocol):
    """Protocol for any LLM API Service used by ACE.

    Defines the interface for processing user queries.
    """

    def __init__(
        self,
        model_name: str,
        system_persona: str,
        actions: Optional[Dict[str, Callable]] = None,
    ):
        """Initialises the API service with a system persona and available actions.

        ### Args
            model_name (str): The name of the model to use.
            system_persona (str): The persona description for the LLM.
            actions (Dict[str, Callable], optional): A dictionary of available actions the LLM can invoke. Defaults to an empty dictionary.
        """

    def __call__(self, user_query: str, chat_history: List[Dict[str, Any]]) -> str:  # type: ignore
        """
        Processes a user query by prompting the LLM, handling tool calls,
        and returning the final conversational response.

        Args:
            user_query (str): The new input from the user.
            chat_history (List[Dict[str, Any]]): The full conversation history.
            output_stream (Any): The stream to output the LLM's response chunks. Defaults to print.

        Returns:
            str: The final conversational response from the LLM.
        """


class GoogleGenAIService:
    """Implementation of the APIService protocol using Google GenAI.

    This class uses the Gemini model with native tool-calling capabilities.
    """

    def __init__(
        self,
        model_name: str,
        system_persona: str,
        actions: Optional[Dict[str, Callable]] = None,
    ):
        """Initialises the GoogleGenAIService with a system persona and available actions.

        ### Args
            model_name (str): The name of the model to use.
            system_persona (str): The persona description for the LLM.
            actions (Optional[Dict[str, ActionHandler]]): A dictionary of available actions the LLM can invoke.
        """
        # Setup variables
        self.model_name = model_name
        self.actions = actions or {}

        # Load LLM
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")

        self.client = genai.Client(api_key=api_key)

        # Add table generation instructions to the persona
        table_instructions = (
            "When asked to create a table, you MUST use Markdown formatting. "
            "Ensure that the table has a header row and that the columns are correctly aligned."
        )
        enhanced_persona = f"{system_persona}\n\n{table_instructions}"

        self.generate_content_config = types.GenerateContentConfig(
            system_instruction=enhanced_persona,
            tools=self._create_api_tools(cast(Dict[str, ActionHandler], actions or {})),
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode=types.FunctionCallingConfigMode.AUTO,
                )
            ),
        )

    def __call__(
        self,
        user_query: str,
        chat_history: List[Dict[str, Any]],
    ) -> str:
        """
        Processes a user query by prompting the LLM and returning the final
        conversational response, allowing the model to decide on tool use.

        Args:
            user_query (str): The new input from the user.
            chat_history (List[Dict[str, Any]]): The full conversation history.

        Returns:
            str: The final conversational response or the result of a tool call.
        """
        # Format chat history for the API
        contents = [
            {"role": msg["role"], "parts": [{"text": msg["text"]}]}
            for msg in chat_history
        ]
        contents.append({"role": "user", "parts": [{"text": user_query}]})

        # Initial API call to see if the model wants to use a tool
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=self.generate_content_config,
        )

        candidate = response.candidates[0]
        parts = getattr(candidate.content, "parts", None)

        # Collect all function calls if any exist
        function_calls = []
        if parts:
            function_calls = [
                part.function_call
                for part in parts
                if hasattr(part, "function_call") and part.function_call
            ]

        if function_calls:
            api_results = []
            for function_call in function_calls:
                action_name = function_call.name
                action_args = dict(function_call.args)

                # Execute the requested tool/action
                if action_name in self.actions:
                    handler = self.actions[action_name]
                    try:
                        result = handler(**action_args)
                    except Exception as e:
                        result = f"Error: Could not execute the action '{action_name}'. Reason: {e}"
                else:
                    result = f"Error: The action '{action_name}' is not available."

                # Store the result for potential fallback
                api_results.append(str(result))

                # Append the original function call and the tool's result to the conversation history
                contents.append(
                    {"role": "model", "parts": [{"function_call": function_call}]}
                )
                contents.append(
                    {
                        "role": "function",
                        "parts": [
                            {
                                "function_response": {
                                    "name": action_name,
                                    "response": {"result": result},
                                }
                            }
                        ],
                    }
                )

            # Second API call to get a conversational response based on the tool's output
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=self.generate_content_config,
            )
            candidate = response.candidates[0]
            parts = getattr(candidate.content, "parts", None)

        # Extract the final text response
        if parts:
            text_parts = [
                part.text
                for part in parts
                if hasattr(part, "text") and part.text is not None
            ]
            text_response = " ".join(text_parts).strip()
        else:
            text_response = ""

        if text_response:
            return text_response

        # Fallback for cases where the response might be in a different format
        # Safely access response.text only if no tool calls were made in the first place
        if not function_calls and response.text:
            return response.text

        # Fallback: If no conversational response, return the raw tool result
        if "api_results" in locals() and api_results:
            return "\n".join(api_results)

        return "No response from LLM."

    def _create_api_tools(self, actions: Dict[str, ActionHandler]) -> List[types.Tool]:
        """Creates API tools for the Gemini model based on the provided actions.

        ### Args
            actions (Dict[str, ActionHandler]): A dictionary of available actions.

        ### Returns
            List[types.Tool]: A list of tools compatible with the Gemini model.
        """
        api_tools = []

        for action_name, handler in actions.items():
            # Skip actions that are meant to be handled internally (e.g., general enquiry fallback)
            if action_name in ["GENERAL_ENQUIRY", "UNKNOWN_ACTION"]:
                continue

            # --- Argument Structure Mapping (Manual/Explicit Definition is Safest) ---
            parameters = {}
            required_params = []

            if action_name == "GET_WEATHER":
                parameters["location"] = types.Schema(
                    type=types.Type.STRING,
                    description="The specific city or location for the weather query (e.g., 'London', 'Paris').",
                )
                required_params.append("location")

            if action_name == "ROLL_DICE":
                parameters["sides"] = types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(
                        type=types.Type.INTEGER,
                        description="Number of sides on the die to roll.",
                    ),
                    description="A list of integers representing the number of sides for each die to roll (e.g., [6] for a single 6-sided die, [6, 8] for rolling both a 6-sided and an 8-sided die).",
                )
                required_params.append("sides")

            if action_name == "WEB_SEARCH":
                parameters["query"] = types.Schema(
                    type=types.Type.STRING,
                    description="The search query for finding real-time information on the web (e.g., 'current news', 'who won the game').",
                )
                required_params.append("query")

            if action_name == "GET_TIME":
                parameters["timezone"] = types.Schema(
                    type=types.Type.STRING,
                    description="The timezone for which to get the current time (e.g., 'UTC', 'America/New_York').",
                )
                required_params.append("timezone")

            # Define function declaration
            function_declaration = types.FunctionDeclaration(
                name=action_name,
                description=handler.description,
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties=parameters,
                    required=required_params,
                ),
            )

            # Define tool object
            tool = types.Tool(function_declarations=[function_declaration])
            api_tools.append(tool)

        return api_tools


class ConversationNamer:
    """An LLM based tool to name a chat topic."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemma-3-27b-it"

    def __call__(self, query: str) -> str:
        """Generates a concise name for the chat based on the query.

        ### Args
            query (str): The chat history as a single string.

        ### Returns
            str: A concise name for the chat topic.
        """
        # The prompt is now constructed here, as Gemma models
        # expect instructions within the 'contents'.
        prompt_instructions = """ROLE AND TASK:
You are an AI Chat Naming Specialist. Your *only* task is to generate a concise, descriptive title for the provided chat history (QUERY).

RULES:
1.  The title *must* be 3 words or less.
2.  The title *must* accurately summarize the main topic.
3.  Do *not* use generic names like 'Chat', 'Conversation', or 'Query'.
4.  You *must* respond ONLY with the title. Do not add any preamble, explanation, or conversational text (e.g., "Here is the name:").

GOOD EXAMPLES:
- "Global News Update"
- "AI Innovations"
- "Cooking Recipes"
- "US Government Discussion"
- "Current Prime Minister"
"""

        # We combine the instructions, the query, and the final cue.
        contents = f"""{prompt_instructions}
QUERY: {query}
NAME:
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=1.5,
                ),
            )

            candidate = response.candidates[0]
            parts = getattr(candidate.content, "parts", None)

            # Extract the final text response
            if parts:
                text_response = " ".join(
                    getattr(part, "text", "")
                    for part in parts
                    if hasattr(part, "text") and getattr(part, "text", None) is not None
                ).strip()

            else:
                text_response = ""

            if text_response:
                # Remove multiple spaces and ensure clean output
                text_response = re.sub(r"\s{2,}", " ", text_response).strip()
                return text_response

            return "Unnamed Chat"

        except Exception as e:
            return f"An error occurred during conversation naming: {e.__class__.__name__} - {str(e)}"
