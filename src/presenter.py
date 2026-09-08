"""The presenter module handles the interaction between the model and view."""

import json
import logging
from typing import Callable, Protocol

from src.storage import ConversationStorage

logger = logging.getLogger(__name__)


class Model(Protocol):
    """A model deals with the business logic of the application."""

    model_name: str
    session_id: str | None = None

    def process_text(self, text: str) -> str: ...

    def load_session(self, session_id: str) -> None: ...

    def start_new_session(self) -> None: ...


class View(Protocol):
    """A view is responsible for displaying information to the user and capturing user input."""

    on_submit: Callable[[str], None] | None
    on_model_change: Callable[[str], None] | None
    on_session_selected: Callable[[str], None] | None
    on_new_chat: Callable[[], None] | None

    def display_text(self, text: str) -> None: ...

    def show_loading(self) -> None: ...

    def hide_loading(self) -> None: ...

    def display_error(self, message: str) -> None: ...

    def populate_sessions(self, sessions: list[str]) -> None: ...

    def clear_chat(self) -> None: ...


class Presenter:
    """The Presenter class acts as an intermediary between the model and view."""

    def __init__(
        self, model: Model, view: View, conversation_storage: ConversationStorage
    ):
        """Initialise the presenter with a model and a view.

        Args:
            model (Model): The model instance to interact with.
            view (View): The view instance to interact with.
            conversation_storage (ConversationStorage): The conversation storage instance to interact with.
        """
        self.model = model
        self.view = view
        self.conversation_storage = conversation_storage

        logger.debug(
            "presenter_initialised session_id=%s model_name=%s",
            getattr(self.model, "session_id", None),
            getattr(self.model, "model_name", None),
        )

        # Connect the view to the presenter
        self.view.on_submit = self.handle_submit
        self.view.on_model_change = self.handle_model_change
        self.view.on_session_selected = self.handle_session_selected
        self.view.on_new_chat = self.handle_new_chat

        # Populate the view with recent sessions from the conversation storage
        recent_sessions = self.conversation_storage.get_recent_sessions()
        self.view.populate_sessions(recent_sessions)

    def handle_submit(self, text: str) -> None:
        """Handle the event when the user submits text through the view.

        Args:
            text (str): The text submitted by the user.
        """
        # Return silently if no text is provided
        if not text.strip():
            logger.debug(
                "discarding_empty_input session_id=%s model_name=%s",
                getattr(self.model, "session_id", None),
                getattr(self.model, "model_name", None),
            )
            return

        # Display the user's message immediately.
        self.view.display_text(f"## You:\n\n{text}\n\n")

        # Show a loading indicator while processing the text
        self.view.show_loading()

        try:
            # Process the text using the model
            result = self.model.process_text(text)

            # Hide the loading indicator after processing
            self.view.hide_loading()

        except Exception as e:
            # Handle any errors that occur during processing
            logger.error(
                "processing_error session_id=%s model_name=%s error_type=%s",
                getattr(self.model, "session_id", None),
                getattr(self.model, "model_name", None),
                type(e).__name__,
                exc_info=True,
            )

            self.view.hide_loading()
            self.view.display_error(f"[ERROR] {str(e)}\n\n")
            return

        # Display the processed text in the view
        self.view.display_text(f"## ACE:\n\n{result}\n\n")

        # Refresh the list of recent sessions in the view
        self.view.populate_sessions(self.conversation_storage.get_recent_sessions())

    def handle_model_change(self, model_name: str) -> None:
        """Handle the event when the user changes the model selection in the view.

        Args:
            model_name (str): The name of the newly selected model.
        """
        # Update the model's name to reflect the new selection
        self.model.model_name = model_name
        logger.info(
            "model_changed session_id=%s model_name=%s",
            getattr(self.model, "session_id", None),
            getattr(self.model, "model_name", None),
        )

    def handle_session_selected(self, session_id: str) -> None:
        """Handle the event when the user selects a session in the view.

        Args:
            session_id (str): The ID of the selected session.
        """
        self.model.load_session(session_id)
        messages = self.conversation_storage.get_session_messages(session_id)

        self.view.clear_chat()
        for message in messages:
            # Filter out system instructions and tool artifacts
            if message["role"] == "system" or not message.get("content"):
                continue

            sender = "You" if message["role"] == "user" else "ACE"
            content = message["content"]

            self.view.display_text(f"## {sender}:\n\n{content}\n\n")

        logger.info(
            "session_selected session_id=%s message_count=%d",
            session_id,
            len(messages),
        )

    def handle_new_chat(self) -> None:
        """Handle the event when the user starts a new chat in the view."""
        logger.debug(
            "new_chat_started previous_session_id=%s",
            self.model.session_id,
        )

        self.model.start_new_session()
        self.view.clear_chat()
