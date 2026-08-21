"""The model module handles the business logic of the application."""

import json
import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from src.tools import Tool

load_dotenv()

FALLBACK_RESPONSES = {
    "content_filter": "I am unable to assist with that particular request.",
    "length": "My response was cut short due to length constraints. Would you like me to continue?",
    "tool_silent": "Action completed, though I have nothing further to report.",
    "default": "I am not sure how to answer that.",
}


class GroqModel:
    """A model deals with the business logic of the application."""

    def __init__(
        self,
        groq: Groq,
        model_name: str = "openai/gpt-oss-120b",
        system_prompt: str | None = None,
        tools: list[Tool] | None = None,
        max_orchestration_loops: int = 5,
    ) -> None:
        """Initialise the model with a Groq instance.

        Args:
            groq (Groq): An instance of the Groq class for processing text.
                Defaults to "openai/gpt-oss-120b" if not specified.
            system_prompt (str | None): An optional system prompt to initialise
                the model's message history
            model_name (str): The name of the model to use for processing text.
            tools (list[Tool] | None): An optional list of tools that the model can use.
        """
        self.client = groq
        self.model_name = model_name

        self.tools = {tool.name: tool for tool in tools} if tools else {}

        self.messages = []

        if system_prompt:
            self._append_message("system", system_prompt)

        self.max_orchestration_loops = max_orchestration_loops

    def _append_message(
        self, role: str, content: str, tool_calls: list[dict[str, Any]] | None = None
    ) -> None:
        """Append a message to the model's message history.

        Args:
            role (str): The role of the message sender (e.g., "user", "assistant").
            content (str): The content of the message.
            tool_calls (list[dict[str, Any]] | None): Optional tool call information to include
                in the message.
        """
        message = {}

        message["role"] = role
        message["content"] = content

        if tool_calls:
            message["tool_calls"] = tool_calls

        self.messages.append(message)

    def _resolve_empty_content(
        self, choice: object, was_tool_call: bool = False
    ) -> str:
        """Determine the appropriate fallback message based on finish_reason."""
        finish_reason = getattr(choice, "finish_reason", None)

        if finish_reason == "content_filter":
            return FALLBACK_RESPONSES["content_filter"]
        if finish_reason == "length":
            return FALLBACK_RESPONSES["length"]
        if was_tool_call:
            return FALLBACK_RESPONSES["tool_silent"]

        return FALLBACK_RESPONSES["default"]

    def _execute_tool_call(self, tool_call: Any) -> str:
        """Execute a tool call and return the response.

        Args:
            tool_call (Any): The tool call object containing the function name and arguments.

        Returns:
            str: The response from the executed tool.
        """
        # Extract the function name and arguments from the tool call
        function_name = tool_call.function.name
        function_to_call = self.tools.get(function_name)

        if not function_to_call:
            return f"Error: Tool '{function_name}' not not registered."

        try:
            function_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            function_args = {}

        print(f"Executing tool '{function_name}' with arguments: {function_args}")

        # Execute the tool function with the provided arguments
        try:
            function_response = function_to_call.execute(**function_args)
            return (
                json.dumps(function_response)
                if isinstance(function_response, (dict, list))
                else str(function_response)
            )
        except Exception as e:
            return f"Error executing tool '{function_name}': {str(e)}"

    def process_text(self, text: str) -> str:
        """Process the input text using the Groq model and return the response.

        Args:
            text (str): The input text to process.

        Returns:
            str: The response from the model.
        """
        print(f"Using model: {self.model_name}")
        self._append_message("user", text)

        try:
            iterations = 0
            was_tool_call = False

            while iterations < self.max_orchestration_loops:
                iterations += 1

                # Step 1: Make initial API call
                kwargs = {}

                if self.tools:
                    kwargs["tools"] = [t.to_groq_spec() for t in self.tools.values()]

                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=self.messages,
                    **kwargs,
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                # Step 2: Check if the model wants to call tools
                if tool_calls:
                    was_tool_call = True

                    # Add the assistant's response to conversation along with the tool call
                    # information
                    self._append_message(
                        "assistant",
                        response_message.content,
                        [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in tool_calls
                        ],
                    )

                    # Step 3: Execute each tool call
                    for tool_call in tool_calls:
                        function_response = self._execute_tool_call(tool_call)

                        # Add tool response to conversation
                        self.messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": tool_call.function.name,
                                "content": function_response,
                            }
                        )
                    # Continue the loop for the next turn / synthesis pass
                    continue

                # Step 4: If no tool calls, we are done, return the assistant's response
                assistant_response = response_message.content or ""

                if not assistant_response:
                    assistant_response = self._resolve_empty_content(
                        response.choices[0], was_tool_call=was_tool_call
                    )

                self._append_message("assistant", assistant_response)
                return assistant_response

            # If we reach here, it means we exceeded the max orchestration loops
            fallback_msg = "I was unable to complete the request because the tool execution loop limit was reached."
            self._append_message("assistant", fallback_msg)
            return fallback_msg

        except Exception as e:
            self.messages.pop()  # Remove orphaned user message on error
            raise RuntimeError(f"Model API error: {str(e)}") from e


if __name__ == "__main__":
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    model = GroqModel(client)

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat.")
            break

        response = model.process_text(user_input)
        print(f"ACE: {response}")
