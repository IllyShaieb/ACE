"""This is the main entry point for the application."""

import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from PyQt6.QtWidgets import QApplication

from src.model import GroqModel
from src.presenter import Presenter
from src.view import PyQt6View

load_dotenv()


def main():
    """Run the main application.

    This is where the MVP components are instantiated and connected. The application
    starts by creating the model, a view, and a presenter that connects the two. The
    event loop is then started to allow user interaction.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    system_prompt_path = (
        Path(__file__).resolve().parent / "assets" / "prompts" / "system_prompt.md"
    )

    if system_prompt_path.exists():
        with open(system_prompt_path, "r") as f:
            system_prompt = f.read().strip()
    else:
        # Show a warning if the system prompt file is not found, but continue with an empty prompt
        print(
            f"Warning: System prompt file not found at {system_prompt_path}. Continuing with an empty system prompt."
        )
        system_prompt = None

    model = GroqModel(client, system_prompt=system_prompt)

    app = QApplication([])
    view = PyQt6View()

    presenter = Presenter(model=model, view=view)

    view.show()
    app.exec()  # Start the event loop


if __name__ == "__main__":
    main()
