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
UNKNOWN_ACTION_MESSAGE: str = "I'm not sure how to do that."


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

                actions = self.model(user_input)

                if not actions:
                    response = "Sorry, I don't understand."
                    self.view.display_message(ACE_ID, response)
                    add_message(ACE_DATABASE, self.chat_id, ACE_ID, response)
                    continue

                responses = [self._execute_action(action) for action in actions]
                combined_response = " ".join(responses)
                self.view.display_message(ACE_ID, combined_response)
                add_message(ACE_DATABASE, self.chat_id, ACE_ID, combined_response)

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

    def _execute_action(self, action: str) -> str:
        """Executes a given action and returns the corresponding response string.

        ### Args
            action (str): The action to execute, which corresponds to an intent.

        ### Returns
            str: The response string for the executed action.
        """
        now = datetime.now()
        day = now.day
        if 11 <= day <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

        actions = {
            "GREET": "Hello! How can I assist you today?",
            "IDENTIFY": "I am ACE, your personal assistant.",
            "CREATOR": "I was created by Illy Shaieb.",
            "GET_TIME": f"The current time is {now.strftime('%H:%M')}.",
            "GET_DATE": f"Today's date is {now.strftime(f'%A {day}{suffix} %B %Y')}.",
        }

        return actions.get(action, UNKNOWN_ACTION_MESSAGE)
