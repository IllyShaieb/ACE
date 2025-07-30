"""presenter.py: Contains the presenter logic for the ACE program."""

from datetime import datetime
import random
import requests

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


def _handle_unknown() -> str:
    """Handles the UNKNOWN action."""
    return UNKNOWN_ACTION_MESSAGE


def _handle_greet() -> str:
    """Handles the GREET action."""
    return "Hello! How can I assist you today?"


def _handle_identify() -> str:
    """Handles the IDENTIFY action."""
    return "I am ACE, your personal assistant."


def _handle_creator() -> str:
    """Handles the CREATOR action."""
    return "I was created by Illy Shaieb."


def _handle_get_time() -> str:
    """Handles the GET_TIME action."""
    return f"The current time is {datetime.now().strftime('%H:%M')}."


def _handle_get_date() -> str:
    """Handles the GET_DATE action."""
    now = datetime.now()
    day = now.day
    suffix = (
        "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    )
    return f"Today's date is {now.strftime(f'%A {day}{suffix} %B %Y')}."


def _handle_help() -> str:
    """Handles the HELP action."""
    return "I can assist you with various tasks. Try asking me about the time, date, or anything else!"


def _handle_joke() -> str:
    """Handles the JOKE action."""
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        response.raise_for_status()
        joke_data = response.json()
        return f"{joke_data['setup']} — {joke_data['punchline']}"
    except (requests.exceptions.HTTPError, requests.RequestException) as e:
        return f"Sorry, I couldn't fetch a joke right now. Error: {e}"


def _handle_flip_coin() -> str:
    """Handles the FLIP_COIN action."""
    return random.choice(["Heads", "Tails"])


def _handle_roll_die() -> str:
    """Handles the ROLL_DIE action."""
    return str(random.randint(1, 6))


def _execute_action(action: str) -> str:
    """Executes a given action by dispatching it to the appropriate handler.

    ### Args
        action (str): The action to execute, which corresponds to an intent.

    ### Returns
        str: The response string for the executed action.
    """
    action_handlers = {
        "GREET": _handle_greet,
        "IDENTIFY": _handle_identify,
        "CREATOR": _handle_creator,
        "GET_TIME": _handle_get_time,
        "GET_DATE": _handle_get_date,
        "HELP": _handle_help,
        "JOKE": _handle_joke,
        "FLIP_COIN": _handle_flip_coin,
        "ROLL_DIE": _handle_roll_die,
    }

    handler = action_handlers.get(action, _handle_unknown)
    return handler()


class ConsolePresenter:
    """Orchestrates the interaction between the ACE model and console view."""

    def __init__(self, model: ACEModel, view: IACEView):
        """Initialises the ConsolePresenter with the model and view."""
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

                responses = [_execute_action(action) for action in actions]
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


class DesktopPresenter:
    """Orchestrates the interaction between the ACE model and a desktop view."""

    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.chat_id = None

    def run(self):
        """
        Run the desktop application.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} | {INITIALISING_MESSAGE}")
        try:
            create_database(ACE_DATABASE)
        except Exception as e:
            self.view.show_error(f"Failed to initialise database: {e}")
            self.view.show_info(
                "[INFO] ACE cannot start without a functional database. Exiting."
            )
            return

        self.chat_id = start_conversation(ACE_DATABASE)

        self.view.show_info(" ACE ".center(80, "="))
        self.view.show_info("    Welcome to ACE! Type 'exit' to quit.\n\n")

        self.view.display_message(ACE_ID, WELCOME_MESSAGE)
        add_message(ACE_DATABASE, self.chat_id, ACE_ID, WELCOME_MESSAGE)

        # Set the input handler so presenter gets user queries
        self.view.set_input_handler(self.handle_user_input)

        # Start the event loop
        self.view.run()

    def handle_user_input(self, user_input):
        """Handle user input from the view.

        ### Args
            user_input (str): The input provided by the user.
        """
        if self.chat_id is not None:
            add_message(ACE_DATABASE, self.chat_id, USER_ID, user_input)
        else:
            self.view.show_error("Conversation ID is not set. Cannot log message.")

        if user_input.lower() == EXIT_COMMAND:
            self.view.display_message(ACE_ID, GOODBYE_MESSAGE)
            if self.chat_id is not None:
                add_message(ACE_DATABASE, self.chat_id, ACE_ID, GOODBYE_MESSAGE)
            self.view.close()
            return

        actions = self.model(user_input)
        response = self._process_actions(actions)

        self.view.display_message(ACE_ID, response)
        if self.chat_id is not None:
            add_message(ACE_DATABASE, self.chat_id, ACE_ID, response)

    def _process_actions(self, actions) -> str:
        if not actions:
            return UNKNOWN_ACTION_MESSAGE

        responses = [_execute_action(action) for action in actions]
        return " ".join(responses)
