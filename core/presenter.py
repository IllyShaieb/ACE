"""presenter.py: Contains the presenter logic for the ACE program."""

from datetime import datetime

from core.database import add_message, create_database, start_conversation
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
NO_DB_MESSAGE: str = "[INFO] ACE cannot start without a functional database. Exiting."


class ACEPresenter:
    """Orchestrates the interaction between the ACE model and view."""

    def __init__(self, model: ACEModel, view: IACEView):
        """Initialises the ACEPresenter with the model and view."""
        self.model = model
        self.view = view
        self.chat_id = None

    def run(self):
        """Runs the main ACE application loop."""
        if not self._initialise_ace():
            return
        self._conversation_loop()

    def _initialise_ace(self):
        """Initialises the ACE application, including the database."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.view.show_info(f"{timestamp} | {INITIALISING_MESSAGE}")

        try:
            create_database(ACE_DATABASE)
        except Exception as e:
            error_message = f"Failed to initialise database: {e}"
            self.view.show_error(error_message)
            if self.chat_id is not None:
                add_message(
                    ACE_DATABASE, self.chat_id, ACE_ID, f"[ERROR] {error_message}"
                )
            self.view.show_info(NO_DB_MESSAGE)
            return False  # Indicate failure

        self.chat_id = start_conversation(ACE_DATABASE)

        self.view.show_info(" ACE ".center(80, "="))
        self.view.show_info("    Welcome to ACE! Type 'exit' to quit.\n\n")

        self.view.display_message(ACE_ID, WELCOME_MESSAGE)
        add_message(ACE_DATABASE, self.chat_id, ACE_ID, WELCOME_MESSAGE)
        return True  # Indicate success

    def _conversation_loop(self):
        """Manages the continuous conversation loop with the user."""
        while True:
            try:
                user_input = self.view.get_user_input(f"{USER_ID}: ")
                if self.chat_id is not None:
                    add_message(ACE_DATABASE, self.chat_id, USER_ID, user_input)
                else:
                    self.view.show_error(
                        "Conversation ID is not set. Cannot log message."
                    )
                    continue

                if user_input.lower() == EXIT_COMMAND:
                    self.view.display_message(ACE_ID, GOODBYE_MESSAGE)
                    add_message(ACE_DATABASE, self.chat_id, ACE_ID, GOODBYE_MESSAGE)
                    break

                response = self.model(user_input)
                self.view.display_message(ACE_ID, response)
                add_message(ACE_DATABASE, self.chat_id, ACE_ID, response)

            except Exception as e:
                error_message = (
                    f"An unexpected error occurred: {e}. I'm sorry, please try again."
                )
                self.view.show_error(error_message)
                if self.chat_id is not None:
                    add_message(
                        ACE_DATABASE, self.chat_id, ACE_ID, f"[ERROR] {error_message}"
                    )
                continue
