"""The model module handles the business logic of the application."""

import json
import os

from dotenv import load_dotenv
from groq import Groq

from src.tools import Tool

load_dotenv()


class GroqModel:
    """A model deals with the business logic of the application."""

    def __init__(
        self,
        groq: Groq,
        model_name: str = "openai/gpt-oss-120b",
        system_prompt: str | None = None,
        tools: list[Tool] | None = None,
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

    def _append_message(self, role: str, content: str) -> None:
        """Append a message to the model's message history.

        Args:
            role (str): The role of the message sender (e.g., "user", "assistant").
            content (str): The content of the message.
        """
        self.messages.append({"role": role, "content": content})

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
                # Add the assistant's response to conversation
                self._append_message("assistant", response_message.content)

                # Step 3: Execute each tool call
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = self.tools.get(function_name)
                    function_args = json.loads(tool_call.function.arguments)

                    if function_to_call:
                        function_response = function_to_call.execute(**function_args)
                    else:
                        function_response = f"Error: Tool '{function_name}' not found."

                    # Add tool response to conversation
                    self.messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )

                # Step 4: Get final response from model
                second_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=self.messages,
                )

                if second_response.choices[0].message.content is None:
                    return "No response received after tool execution."

                return second_response.choices[0].message.content

            # If no tool calls, return the direct response (or the fallback string if None)
            return response_message.content or "No response received."

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
