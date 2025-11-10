"""model.py: Contains the core model for the ACE program."""

import os
from pathlib import Path
from typing import Any, Dict, List

from .actions import ACTION_HANDLERS
from .llm import APIService, GoogleGenAIService

# Constants defining the AI's persona for the system prompt
if not os.path.exists("data/PERSONA.md"):
    raise FileNotFoundError("PERSONA.md file not found in data directory.")
with open(os.path.join("data", "PERSONA.md"), "r", encoding="utf-8") as f:
    AI_PERSONA = f.read()


class ACEModel:
    """The main model for the ACE program, managing the single LLM API service.

    This class provides the interface for the Presenter to interact with the LLM.
    It is designed to be independent of the underlying API implementation (GenAI, Ollama, etc.).
    """

    def __init__(self):
        """Initialises the ACEModel with the specified LLM API service."""
        try:
            # Build a robust, absolute path to the persona file.
            # This path is relative to *this* file (model.py), not the execution directory.
            persona_path = Path(__file__).parent.parent / "data" / "PERSONA.md"

            if not persona_path.exists():
                raise FileNotFoundError(f"Persona file not found at: {persona_path}")

            with open(persona_path, "r", encoding="utf-8") as f:
                ai_persona = f.read()

            self.api_service: APIService = GoogleGenAIService(
                model_name="models/gemini-2.5-flash",
                system_persona=ai_persona,
                actions=ACTION_HANDLERS,
            )
        except Exception as e:
            # We can now provide a more specific error
            raise RuntimeError(f"Failed to initialize ACEModel: {e}")

    def __call__(
        self,
        user_input: str,
        chat_history: List[Dict[str, Any]],
    ) -> Any:
        """Processes the user's input using the LLM API service.

        The API service handles intent classification, tool execution, and response generation.

        ### Args
            user_input (str): The user's input to process.
            chat_history (List[dict]): The list of previous messages for context.

        ### Returns
            Any: The final conversational response from the LLM.
        """
        # The API service handles all complex logic.
        return self.api_service(user_input, chat_history)
