"""The model module handles the business logic of the application."""

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class GroqModel:
    """A model deals with the business logic of the application."""

    def __init__(
        self,
        groq: Groq,
        model_name: str = "openai/gpt-oss-120b",
        system_prompt: str | None = None,
    ) -> None:
        """Initialise the model with a Groq instance.

        Args:
            groq (Groq): An instance of the Groq class for processing text.
                Defaults to "openai/gpt-oss-120b" if not specified.
            system_prompt (str | None): An optional system prompt to initialise
                the model's message history
            model_name (str): The name of the model to use for processing text.
        """
        self.client = groq
        self.model_name = model_name

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
            chat_completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.messages,
            )

            chat_response = chat_completion.choices[0].message.content

            # Handle empty/None responses
            if not chat_response:
                self.messages.pop()  # Remove orphaned user message
                return "No response received."

            self._append_message("assistant", chat_response)
            return chat_response

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
