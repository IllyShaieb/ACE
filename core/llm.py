"""llm.py: Handles all interactions with external LLM APIs.

This module defines the APIService protocol for flexible API switching and
provides an implementation for the Google GenAI service with native tool calling.
"""

import os
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
        self.generate_content_config = types.GenerateContentConfig(
            system_instruction=system_persona,
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

        try:

            candidate = response.candidates[0]

            # Check if parts exists before trying to access its elements
            if candidate.content.parts and candidate.content.parts[0].function_call:
                function_call = candidate.content.parts[0].function_call
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
                # Update candidate after second call
                candidate = response.candidates[0]

            # Extract the final text response
            parts = candidate.content.parts

            if parts:
                text_response = " ".join(
                    getattr(part, "text", "") for part in parts if hasattr(part, "text")
                ).strip()
            else:
                text_response = ""

            if text_response:
                return text_response

            # Use str() for robustness, as finish_reason can be an enum
            finish_reason = str(candidate.finish_reason)
            if finish_reason != "STOP":
                return f"I am unable to respond. The request finished unexpectedly (Reason: {finish_reason})."

            return "No response from LLM."

        except Exception as e:
            # Add more detail to the exception
            return (
                f"An unexpected LLM response error occurred: {str(e)} (Type: {type(e)})"
            )

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
