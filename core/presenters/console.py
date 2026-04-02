"""core.presenters.console: This module defines the ConsolePresenter class, which mediates between the
model and console-based view components of the ACE application."""

from typing import Optional

from core.adapters.protocols import (
    ConversationStorageAdapterProtocol,
    LogStorageAdapterProtocol,
)
from core.models.protocols import ModelProtocol
from core.views.protocols import Sender, ViewProtocol


class ConsolePresenter:
    """Presenter for the console-based view, mediating between the model and view."""

    def __init__(
        self,
        model: ModelProtocol,
        view: ViewProtocol,
        welcome_message: str = "",
        storage_adapter: Optional[ConversationStorageAdapterProtocol] = None,
        log_storage_adapter: Optional[LogStorageAdapterProtocol] = None,
    ):
        """Initialize the presenter with the given model and view.

        Args:
            model (ModelProtocol): The model component to interact with.
            view (ViewProtocol): The view component to update based on model changes.
            welcome_message (str): The welcome message to display when the presenter runs.
                Defaults to an empty string if not provided.
            storage_adapter (Optional[ConversationStorageAdapterProtocol]): The storage adapter for conversation sessions.
                Defaults to None if not provided.
            log_storage_adapter (Optional[LogStorageAdapterProtocol]): The storage adapter for log storage.
                Defaults to None if not provided.
        """
        self.model = model
        self.view = view
        self.welcome_message = welcome_message
        self.storage_adapter = storage_adapter
        self.log_storage_adapter = log_storage_adapter

        # Connect view events to presenter methods
        self.view.events.on_user_input.connect(self.handle_user_input)

    def _log_event(
        self, level: str, source: str, message: str, details: Optional[str] = None
    ) -> None:
        """Log an event to the log storage adapter.

        Args:
            level (str): The severity level of the event (e.g., "INFO", "ERROR").
            source (str): The source of the event (e.g., "model", "tool").
            message (str): A descriptive message about the event.
            details (Optional[str]): Additional details or context about the event.
        """
        if self.log_storage_adapter:
            self.log_storage_adapter.log_event(
                level=level, source=source, message=message, details=details
            )

    async def run(self) -> None:
        """Display the welcome message (if any) and start the view."""
        self._log_event(
            level="INFO",
            source="presenter",
            message="Application started. Running presenter.",
        )

        # 1. Display the welcome message FIRST to maintain visual flow
        if self.welcome_message:
            self.view.display_message(Sender.INFO, self.welcome_message)

        # 2. Fetch the 5 most recent sessions
        recent_sessions = (
            self.storage_adapter.get_recent_sessions(limit=5)
            if self.storage_adapter
            else []
        )

        # 3. Ask the view to display them and get the user's choice
        session_id = self.view.get_session_choice(recent_sessions)

        # 4. Tell the model to load the chosen session (or create a new one)
        self.model.load_session(session_id)

        # 5. Print previous history if an old session was selected
        if session_id and self.storage_adapter:
            self._log_event(
                level="INFO",
                source="presenter",
                message=f"Loaded session: {session_id}",
            )

            history = self.storage_adapter.get_session_messages(session_id)
            for msg in history:
                sender = Sender.USER if msg["sender"].lower() == "user" else Sender.ACE
                self.view.display_message(sender, msg["content"])
        else:
            self._log_event(
                level="INFO",
                source="presenter",
                message="No session loaded, starting new session.",
            )

        await self.view.start()

    async def handle_user_input(self, user_input: str) -> None:
        """Process user input and update the view accordingly.

        Args:
            user_input (str): The input received from the user.
        """
        # Sanitise input by stripping whitespace
        cleaned_input = user_input.strip()

        # Ignore empty input as it doesn't require any action
        if not cleaned_input:
            return

        # Check for exit command to stop the view and end the application
        if cleaned_input == "exit":
            self._log_event(
                level="INFO",
                source="presenter",
                message="Exit command received. Stopping presenter.",
            )
            self.view.stop()
            return

        # Process the user input through the model and get a response
        response = await self.view.show_loading(
            "Thinking...",
            self.model.process_query,
            query=cleaned_input,  # type: ignore
        )
        self.view.display_message(
            Sender.ACE, response or "Sorry, I couldn't process that."
        )
