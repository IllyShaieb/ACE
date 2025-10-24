"""presenter.py: Contains the presenter logic for the ACE program."""

from datetime import datetime
from threading import Thread
from typing import List

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
        self.view.display_message("INFO", f"{timestamp} | {INITIALISING_MESSAGE}")

        try:
            create_database(ACE_DATABASE)
        except Exception as e:
            self.view.display_message("ERROR", f"Failed to initialise database: {e}")
            self.view.display_message("INFO", NO_DB_MESSAGE)
            return False  # Indicate failure

        self.view.display_message("INFO", " ACE ".center(80, "="))
        self.view.display_message(
            "INFO", "    Welcome to ACE! Type 'exit' to quit.\n\n"
        )

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
            self.view.display_message(
                "ERROR", "Conversation ID is not set. Cannot log message."
            )
            return True  # Continue running

        # Check for exit command
        if user_input.lower() == EXIT_COMMAND:
            self.view.display_message(ACE_ID, GOODBYE_MESSAGE)
            if self.chat_id is not None:
                add_message(ACE_DATABASE, self.chat_id, ACE_ID, GOODBYE_MESSAGE)
            # self.view.close() # Defer closing for DesktopView
            return False  # Indicate exit

        # Simulate error and info
        if user_input.lower() == "test info":
            self.view.display_message("INFO", "This is an informational message.")

        if user_input.lower() == "test error":
            self.view.display_message("ERROR", "This is an error message.")

        # Process the user input through the model
        actions = self.model(user_input)
        response = self._process_actions(actions, user_input)

        self.view.display_message(ACE_ID, response)
        if self.chat_id is not None:
            add_message(ACE_DATABASE, self.chat_id, ACE_ID, response)
        return True  # Continue running

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
                    # Always pass user_input; let the handler decide if it needs it
                    response = handler_info.handler(user_input)
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
        """
        Processes user input, displays it, gets a response, and displays the response.
        """
        if not user_input:
            return True  # Continue loop if input is empty

        # Display the user's message in a bubble
        self.view.display_message(USER_ID, user_input)

        # Now, process the input and get ACE's response
        return super().process_user_input(user_input)

    def show_termination_message(self):
        """Displays the termination message."""
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
        """The target function for the input processing thread."""
        # If this is the first message, a new conversation will be created.
        # We need to refresh the history to show it.
        new_conversation = self.chat_id is None
        try:
            should_continue = self.process_user_input(user_input)
            if not should_continue:
                # Schedule the window to close safely after 100ms
                self.view.after(100, self.view.close)
        except Exception as e:
            self.view.display_message("ERROR", f"An error occurred: {e}")

        if new_conversation:
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
        self.view.display_message("INFO", f"{timestamp} | {INITIALISING_MESSAGE}")

        self.view.display_message("INFO", " ACE ".center(80, "="))
        self.view.display_message(
            "INFO", "    Welcome to ACE! Type 'exit' to quit.\n\n"
        )

        messages = get_messages(ACE_DATABASE, self.chat_id)
        for msg in messages:
            # msg format: (message_id, conversation_id, sender, content, timestamp)
            sender = msg[2]
            content = msg[3]
            self.view.display_message(sender, content)

        self.view.scroll_to_bottom()

    def start_new_conversation(self):
        """Starts a new chat session."""
        self.chat_id = None
        self.view.clear_chat_history()

        # Display initial info messages for context
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.view.display_message("INFO", f"{timestamp} | {INITIALISING_MESSAGE}")

        self.view.display_message("INFO", " ACE ".center(80, "="))
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
