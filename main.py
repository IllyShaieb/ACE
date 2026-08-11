"""This is the main entry point for the application."""

from typing import Callable, NoReturn, TypedDict

from PyQt6.QtWidgets import QApplication

from src.presenter import Presenter
from src.view import PyQt6View


class PatternEntry(TypedDict):
    pattern: str
    function: Callable[[], str]


class MockModel:
    """A mock model class for demonstration purposes."""

    def process_text(self, text: str) -> str:
        """Simulate processing the input text and returning a result.

        Args:
            text (str): The input text to process.

        Returns:
            str: A processed version of the input text.
        """
        import re
        from random import random
        from time import sleep

        print(f"Processing text: {text}")

        sleep(random() * 0.5)  # Simulate a delay in processing

        # Simulate a basic pattern matching process to demonstrate functionality
        patterns: dict[str, PatternEntry] = {
            "greeting": {
                "pattern": r"\b(hello|hi|hey)\b",
                "function": self._greeting,
            },
            "farewell": {
                "pattern": r"\b(bye|goodbye|see you)\b",
                "function": self._farewell,
            },
            "question": {
                "pattern": r"\b(what|how|why|when|where)\b",
                "function": self._question,
            },
            "identification": {
                "pattern": r"\b(who|name|identify)\b",
                "function": self._identification,
            },
            "error": {
                "pattern": r"\b(error|fail|problem)\b",
                "function": self._error,
            },
        }

        for _, pattern_entry in patterns.items():
            regex_pattern: str = pattern_entry["pattern"]
            if re.search(regex_pattern, text, re.IGNORECASE):
                return pattern_entry["function"]()
        return "Sorry, I don't know what you mean."

    def _greeting(self) -> str:
        """Return a greeting message."""
        return "Hello! I am ACE, your AI assistant. How can I help you today?"

    def _farewell(self) -> str:
        """Return a farewell message."""
        return "Goodbye! Have a great day!"

    def _question(self) -> str:
        """Return a generic response to a question."""
        return "That's an interesting question. Let me think about it."

    def _identification(self) -> str:
        """Return an identification message."""
        return "I am ACE, your AI assistant."

    def _error(self) -> NoReturn:
        """A helper function to simulate an error for demonstration purposes."""
        raise Exception(
            "Simulated error: something went wrong while processing your text."
        )


def main():
    """Run the main application.

    This is where the MVP components are instantiated and connected. The application
    starts by creating the model, a view, and a presenter that connects the two. The
    event loop is then started to allow user interaction.
    """
    model = MockModel()
    app = QApplication([])
    view = PyQt6View()

    presenter = Presenter(model=model, view=view)

    view.show()
    app.exec()  # Start the event loop


if __name__ == "__main__":
    main()
