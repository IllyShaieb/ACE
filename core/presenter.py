"""presenter.py: Contains the presenter logic for the ACE program."""

from datetime import datetime
from threading import Thread
from typing import Any, Dict, List, Optional

from core.actions import ACTION_HANDLERS, UNKNOWN_ACTION_MESSAGE
from core.database import (
    add_message,
    create_database,
    delete_conversation,
    get_conversations,
    get_messages,
    start_conversation,
)
from core.model import ACEModel
from core.view import IACEView

# Constants for ACE and user identification, and the exit command
ACE_ID: str = "ACE"
USER_ID: str = "YOU"
EXIT_COMMAND: str = "exit"
ACE_DATABASE: str = "data/ace.db"
WELCOME_MESSAGE: str = (
    "Hello! I am ACE, your personal assistant. How can I help you today?"
)
GOODBYE_MESSAGE: str = "Goodbye! It was a pleasure assisting you."
INITIALISING_MESSAGE: str = "Initialising ACE"
TERMINATION_MESSAGE: str = "Terminating ACE"
NO_DB_MESSAGE: str = "[INFO] ACE cannot start without a functional database. Exiting."
EMPTY_RESPONSE_MESSAGE: str = "I'm sorry, I don't have a response for that."


class BasePresenter:
    """Base class for orchestrating the interaction between the ACE model and the view."""

    def __init__(self, model: ACEModel, view: IACEView):
        """Initialises the presenter with the model and view.

        ### Args
            model (ACEModel): The model instance that contains the business logic.
            view (IACEView): The view instance that handles user interaction.
        """
        self.model = model
        self.view = view
        self.chat_id = None

    def initialise(self):
        """Initialises the ACE application, including the database and API."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.view.display_message("INFO", f"{timestamp} | {INITIALISING_MESSAGE}")

        try:
            create_database(ACE_DATABASE)
        except Exception as e:
            self.view.display_message("ERROR", f"Failed to initialise database: {e}")
            self.view.display_message("INFO", NO_DB_MESSAGE)
            return False  # Indicate failure

        self.view.display_message(
            "INFO", "    Welcome to ACE! Type 'exit' to quit.\n\n"
        )

        self.view.display_message(ACE_ID, WELCOME_MESSAGE)

        return True  # Indicate success

    def process_user_input(
        self, user_input: str, display_user_message: bool = True
    ) -> bool:
        """Processes user input, gets a response, and displays it.

        ### Args
            user_input (str): The input provided by the user.
            display_user_message (bool): Whether to display the user's message in the view.

        ### Returns
            bool: True if processing was successful, False otherwise.
        """
        if not user_input:
            return True

        # If this is the first user message, create the conversation and save the welcome message
        if self.chat_id is None:
            self.chat_id = start_conversation(ACE_DATABASE)
            add_message(ACE_DATABASE, self.chat_id, ACE_ID, WELCOME_MESSAGE)

        # 1. Display user's message immediately
        if display_user_message:
            self.view.display_message(USER_ID, user_input)

        # 2. Load PAST chat history (does not include the current user_input)
        chat_history = self._load_chat_history(self.chat_id)

        # 3. Get ACE's response from the model
        response = self.view.track_action(lambda: self.model(user_input, chat_history))

        # 4. Display ACE's response
        final_response = response or EMPTY_RESPONSE_MESSAGE
        self.view.display_message(ACE_ID, final_response)

        # 5. Log the complete exchange to the database
        if self.chat_id is not None:
            add_message(ACE_DATABASE, self.chat_id, USER_ID, user_input)
            add_message(ACE_DATABASE, self.chat_id, ACE_ID, final_response)

        return True  # Continue running

    def _load_chat_history(self, chat_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Loads and formats the current chat history from the database.

        ### Args
            chat_id (Optional[int]): The ID of the chat conversation to load.
        """
        if chat_id is None:
            return []

        messages = get_messages(ACE_DATABASE, chat_id)

        # Format for the LLM API
        formatted_history = []
        for sender, message, _ in messages:
            role = "model" if sender == ACE_ID else "user"
            formatted_history.append({"role": role, "text": message})

        return formatted_history

    def _process_actions(self, actions: List[str], user_input: str) -> str:
        """Processes actions and shows a typing indicator in the console.

        ### Args
            actions (List[str]): A list of actions to process.
            user_input (str): The user input to pass to the action handlers.

        ### Returns
            str: A string containing the responses for the processed actions.
        """

        def do_actions():

            # No actions detected
            if not actions:
                return UNKNOWN_ACTION_MESSAGE

            # Process each action and collect responses
            responses = []
            for action in actions:
                if action in ACTION_HANDLERS:
                    handler_info = ACTION_HANDLERS[action]

                    # Check if the handler requires user input
                    if handler_info.requires_user_input:
                        response = handler_info.handler(user_input)
                    else:
                        response = handler_info.handler()
                    responses.append(response)

            # All actions unrecognised
            if not responses:
                return UNKNOWN_ACTION_MESSAGE

            return " ".join(responses)

        # Use the view's track_action to show a spinner during execution
        return self.view.track_action(do_actions, "ACE is typing...")

    def show_termination_message(self):
        """Displays the termination message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.view.display_message("INFO", f"{timestamp} | {TERMINATION_MESSAGE}")


class ConsolePresenter(BasePresenter):
    """Orchestrates the interaction between the ACE model and console view."""

    def run(self):
        """Runs the main ACE application loop."""
        if self.initialise():
            while True:
                user_input = self.view.get_user_input(f"{USER_ID}: ")
                self.view.clear_input()
                if not self.process_user_input(user_input):
                    self.view.close()
                    break

        self.show_termination_message()

    def process_user_input(self, user_input: str) -> bool:
        """Overrides the base implementation to handle console-specific logic.

        This method ensures that the application continues to run unless the user
        explicitly types the exit command.

        ### Args:
            user_input (str): The input from the user.

        ### Returns:
            bool: True if the application should continue, False if it should exit.
        """
        if user_input.lower() == EXIT_COMMAND:
            return False

        # Call the base presenter's logic to handle the core processing
        super().process_user_input(user_input)

        # Always return True to keep the console application running
        return True

    def show_termination_message(self):
        """Displays the termination message in the console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.view.display_message("INFO", f"{timestamp} | {TERMINATION_MESSAGE}")


class DesktopPresenter(BasePresenter):
    """Orchestrates the interaction between the ACE model and a desktop view."""

    def run(self):
        """Run the desktop application."""
        if self.initialise():
            self.view.set_input_handler(self.handle_user_input)
            self._load_and_display_conversations()
            self.view.run()

    def handle_user_input(self, user_input: str):
        """Handle user input from the view by running it in a separate thread.

        ### Args
            user_input (str): The input provided by the user.
        """
        # Run the processing in a separate thread to avoid blocking the GUI
        thread = Thread(
            target=self._process_input_thread, args=(user_input,), daemon=True
        )
        thread.start()

    def _process_input_thread(self, user_input: str):
        """The target function for the input processing thread.

        ### Args
            user_input (str): The input provided by the user.
        """
        new_conversation = self.chat_id is None

        try:
            # 1. Display user message (Scheduled on main thread)
            # This view's _send_message does not display, so presenter must.
            self.view.after(0, lambda: self.view.display_message(USER_ID, user_input))

            # 2. Start database conversation if needed
            if self.chat_id is None:
                self.chat_id = start_conversation(ACE_DATABASE)
                add_message(ACE_DATABASE, self.chat_id, ACE_ID, WELCOME_MESSAGE)

            # 3. Load history
            chat_history = self._load_chat_history(self.chat_id)

            # 4. Get response from model (This is the blocking call)
            # We wrap this in track_action, which is now handled by the presenter

            def get_model_response():
                return self.model(user_input, chat_history)

            # Use view.track_action to manage indicators *around the blocking call*
            response = self.view.track_action(get_model_response)
            final_response = response or EMPTY_RESPONSE_MESSAGE

            # 5. Log to DB
            add_message(ACE_DATABASE, self.chat_id, USER_ID, user_input)
            add_message(ACE_DATABASE, self.chat_id, ACE_ID, final_response)

            # 6. Schedule ACE response (Scheduled on main thread)
            self.view.after(
                0, lambda: self.view.display_message(ACE_ID, final_response)
            )

            if new_conversation:
                # Schedule conversation list refresh on main thread
                self.view.after(0, self._load_and_display_conversations)

            # Ensure typing indicator is hidden after processing
            self.view.after(0, self.view.hide_typing_indicator)

        except Exception as e:
            # Schedule error display back on the main thread
            error_message = f"An error occurred: {e}"
            self.view.after(
                0, lambda: self.view.display_message("ERROR", error_message)
            )
            # Ensure indicator is hidden on error
            self.view.after(0, self.view.hide_typing_indicator)

    def select_conversation(self, conversation_id: int):
        """Handles the selection of a conversation from the history.

        ### Args
            conversation_id (int): The ID of the conversation to select.
        """
        self.chat_id = conversation_id
        self.view.clear_chat_history()

        # Display initial info messages for context
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.view.display_message("INFO", f"{timestamp} | {INITIALISING_MESSAGE}")
        self.view.display_message(
            "INFO", "    Welcome to ACE! Type 'exit' to quit.\n\n"
        )

        messages = get_messages(ACE_DATABASE, self.chat_id)

        history_for_view = [(sender, message) for sender, message, _ in messages]
        for sender, message in history_for_view:
            self.view.display_message(sender, message)

    def _load_and_display_conversations(self):
        """Loads conversations from the database and displays them in the view."""
        conversations = get_conversations(ACE_DATABASE)
        self.view.display_conversations(
            conversations,
            self.select_conversation,
            self.delete_conversation,
            self.start_new_conversation,
        )

    def start_new_conversation(self):
        """Starts a new chat session."""
        self.chat_id = None
        self.view.clear_chat_history()

        # Display initial info messages for context
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.view.display_message("INFO", f"{timestamp} | {INITIALISING_MESSAGE}")
        self.view.display_message(
            "INFO", "    Welcome to ACE! Type 'exit' to quit.\n\n"
        )

        self.view.display_message(ACE_ID, WELCOME_MESSAGE)

    def delete_conversation(self, conversation_id: int):
        """Deletes a conversation after user confirmation."""
        if self.view.show_confirmation(
            "Delete Conversation",
            f"Are you sure you want to delete conversation {conversation_id}?",
        ):
            delete_conversation(ACE_DATABASE, conversation_id)
            self._load_and_display_conversations()
            # If the deleted chat was the active one, start a new chat
            if self.chat_id == conversation_id:
                self.start_new_conversation()
