"""presenter.py: Contains the presenter logic for the ACE program."""

from datetime import datetime
import random
from typing import List
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

        responses = [_execute_action(action) for action in actions]
        return " ".join(responses)


class ConsolePresenter(BasePresenter):
    """Orchestrates the interaction between the ACE model and console view."""

    def run(self):
        """Runs the main ACE application loop."""
        if not self.initialise():
            return
        while True:
            user_input = self.view.get_user_input(f"{USER_ID}: ")
            if not self.process_user_input(user_input):
                break


class DesktopPresenter(BasePresenter):
    """Orchestrates the interaction between the ACE model and a desktop view."""

    def run(self):
        """Run the desktop application."""
        if not self.initialise():
            return

        # Set the input handler so presenter gets user queries
        self.view.set_input_handler(self.handle_user_input)

        # Start the event loop
        self.view.run()

    def handle_user_input(self, user_input: str):
        """Handle user input from the view.

        ### Args
            user_input (str): The input provided by the user.
        """
        self.process_user_input(user_input)
