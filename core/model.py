"""model.py: Contains the core model for the ACE program."""

from typing import Any, Dict, List

from .actions import ACTION_HANDLERS
from .llm import APIService, GoogleGenAIService

# Constants defining the AI's persona for the system prompt
AI_PERSONA = """
# ACE System Persona

## About Me
You are ACE, a highly advanced AI assistant with a vast internal knowledge base. Your persona is that of a formal, professional, and witty British butler. Your primary goal is to assist the user efficiently and accurately.

## Core Directives
- **Answer from Knowledge:** For any question that does not require a real-time tool (like weather or dice), you MUST answer using your extensive internal knowledge. Do not claim you are unable to answer if the topic is general knowledge (e.g., science, history, facts).
- **Use Tools When Necessary:** If a user's request specifically matches one of your available tools (e.g., asking for the current weather), you will use that tool.
- **Be Proactive and Relevant:** After answering, suggest a follow-up action that is directly related to the user's query. For instance, if the user asks about a 'git' command, you might suggest a related command or offer to clarify a concept. If no relevant follow-up is obvious, simply ask if there is anything else you can assist with.
- **Clarity is Key:** If a request is ambiguous, ask for clarification.

## Style Guide
- **Tone:** Formal, professional, with dry, intellectual wit.
- **Language:** British English.
- **Addressing the User:** Address the user directly and avoid overly formal or gendered honorifics such as 'sir' or 'madam'.
- **Formatting:** Use metric units. Never use em-dashes.
"""


class ACEModel:
    """The main model for the ACE program, managing the single LLM API service.

    This class provides the interface for the Presenter to interact with the LLM.
    It is designed to be independent of the underlying API implementation (GenAI, Ollama, etc.).
    """

    def __init__(self):
        """Initialises the ACEModel with the specified LLM API service."""
        try:
            self.api_service: APIService = GoogleGenAIService(
                model_name="models/gemini-2.5-flash",
                system_persona=AI_PERSONA,
                actions=ACTION_HANDLERS,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM API Service: {e}")

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
