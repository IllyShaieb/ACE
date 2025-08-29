"""presenter.py: Contains the presenter logic for the ACE program."""

from datetime import datetime
from threading import Thread
from typing import List

from core.actions import UNKNOWN_ACTION_MESSAGE, execute_action
from core.database import (add_message, create_database, delete_conversation,
                           get_conversations, get_messages, start_conversation)
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
        """Initialises the ACE application, including the database."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.view.show_info(f"{timestamp} | {INITIALISING_MESSAGE}")

        try:
            create_database(ACE_DATABASE)
        except Exception as e:
            self.view.show_error(f"Failed to initialise database: {e}")
            self.view.show_info(NO_DB_MESSAGE)
            return False  # Indicate failure

        self.view.show_info(" ACE ".center(80, "="))
        self.view.show_info("    Welcome to ACE! Type 'exit' to quit.\n\n")

        self.view.display_message(ACE_ID, WELCOME_MESSAGE)
        return True  # Indicate success

    def process_user_input(self, user_input: str) -> bool:
        """Processes the user input and generates a response.

        ### Args
            user_input (str): The input provided by the user.

        ### Returns
            bool: True if the application should continue running, False if it should exit.
        """
        # If no chat is active, start a new one and log the initial messages
        if self.chat_id is None:
            self.chat_id = start_conversation(ACE_DATABASE)
            add_message(ACE_DATABASE, self.chat_id, ACE_ID, WELCOME_MESSAGE)

        # Log the user input
        if self.chat_id is not None:
            add_message(ACE_DATABASE, self.chat_id, USER_ID, user_input)
        else:
            self.view.show_error("Conversation ID is not set. Cannot log message.")
            return True  # Continue running

        # Check for exit command
        if user_input.lower() == EXIT_COMMAND:
            self.view.display_message(ACE_ID, GOODBYE_MESSAGE)
            if self.chat_id is not None:
                add_message(ACE_DATABASE, self.chat_id, ACE_ID, GOODBYE_MESSAGE)
            self.view.close()
            return False  # Indicate exit

        # Process the user input through the model
        actions = self.model(user_input)
        response = self._process_actions(actions)

        # Hide typing indicator and display response
        self.view.hide_typing_indicator()
        self.view.display_message(ACE_ID, response)
        if self.chat_id is not None:
            add_message(ACE_DATABASE, self.chat_id, ACE_ID, response)
        return True  # Continue running

    def _process_actions(self, actions: List[str]) -> str:
        """Processes the actions returned by the model and generates a response string.

        ### Args
            actions (List[str]): A list of actions to process.

        ### Returns
            str: A string containing the responses for the processed actions.
        """
        if not actions:
            return UNKNOWN_ACTION_MESSAGE

        responses = [execute_action(action) for action in actions]
        return " ".join(responses)

    def show_termination_message(self):
        """Displays the termination message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.view.show_info(f"{timestamp} | {TERMINATION_MESSAGE}")


class ConsolePresenter(BasePresenter):
    """Orchestrates the interaction between the ACE model and console view."""

    def run(self):
        """Runs the main ACE application loop."""
        if self.initialise():
            while self.process_user_input(self.view.get_user_input(f"{USER_ID}: ")):
                pass

        self.show_termination_message()


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
        # Show typing indicator immediately
        self.view.show_typing_indicator()

        # Run the processing in a separate thread to avoid blocking the GUI
        thread = Thread(target=self._process_input_thread, args=(user_input,))
        thread.start()

    def _process_input_thread(self, user_input: str):
        """The target function for the input processing thread."""
        # If this is the first message, a new conversation will be created.
        # We need to refresh the history to show it.
        new_conversation = self.chat_id is None

        self.process_user_input(user_input)

        if new_conversation:
            # This needs to be done in the main thread if it updates the GUI
            self.view.after(0, self._load_and_display_conversations)

    def _load_and_display_conversations(self):
        """Loads conversations from the database and displays them in the view."""
        conversations = get_conversations(ACE_DATABASE)
        self.view.display_conversations(
            conversations,
            self.select_conversation,
            self.delete_conversation,
            self.start_new_conversation,
        )

    def select_conversation(self, conversation_id: int):
        """Handles the selection of a conversation from the history."""
        self.chat_id = conversation_id
        self.view.clear_chat_history()

        # Display initial info messages for context
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.view.show_info(f"{timestamp} | {INITIALISING_MESSAGE}")

        self.view.show_info(" ACE ".center(80, "="))
        self.view.show_info("    Welcome to ACE! Type 'exit' to quit.\n\n")

        messages = get_messages(ACE_DATABASE, self.chat_id)
        for msg in messages:
            # msg format: (message_id, conversation_id, sender, content, timestamp)
            sender = msg[2]
            content = msg[3]
            self.view.display_message(sender, content)

    def start_new_conversation(self):
        """Starts a new chat session."""
        self.chat_id = None
        self.view.clear_chat_history()
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
