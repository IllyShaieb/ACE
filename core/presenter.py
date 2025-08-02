"""presenter.py: Contains the presenter logic for the ACE program."""

from datetime import datetime
from typing import List

from core.database import add_message, create_database, start_conversation
from core.model import ACEModel
from core.view import IACEView
from core.actions import execute_action, UNKNOWN_ACTION_MESSAGE

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

        self.chat_id = start_conversation(ACE_DATABASE)

        self.view.show_info(" ACE ".center(80, "="))
        self.view.show_info("    Welcome to ACE! Type 'exit' to quit.\n\n")

        self.view.display_message(ACE_ID, WELCOME_MESSAGE)
        add_message(ACE_DATABASE, self.chat_id, ACE_ID, WELCOME_MESSAGE)
        return True  # Indicate success

    def process_user_input(self, user_input: str) -> bool:
        """Processes the user input and generates a response.

        ### Args
            user_input (str): The input provided by the user.

        ### Returns
            bool: True if the application should continue running, False if it should exit.
        """
        # Log the user input
        if self.chat_id is not None:
            add_message(ACE_DATABASE, self.chat_id, USER_ID, user_input)
        else:
            self.view.show_error("Conversation ID is not set. Cannot log message.")

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
            self.view.run()

        self.show_termination_message()

    def handle_user_input(self, user_input: str):
        """Handle user input from the view.

        ### Args
            user_input (str): The input provided by the user.
        """
        self.process_user_input(user_input)
