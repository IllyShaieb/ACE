"""actions.py: Contains the functions for handling actions in the ACE program."""

import random
from datetime import datetime
import requests
from typing import Callable

UNKNOWN_ACTION_MESSAGE = "I'm not sure how to do that."

# Registry for action handlers
ACTION_HANDLERS = {}


def register_handler(name: str) -> Callable[[Callable], Callable]:
    """Decorator to register an action handler and add it to the ACTION_HANDLERS
    dictionary. This allows for easy addition of new actions without modifying the
    execute_action function.

    ### Args
        name (str): The name of the action to register.

    ### Returns
        function: The decorated function that handles the action.
    """

    def decorator(func: Callable) -> Callable:
        """Add the function to the ACTION_HANDLERS dictionary.

        ### Args
            func (Callable): The function to register as an action handler.

        ### Returns
            function: The original function.
        """
        ACTION_HANDLERS[name] = func
        return func

    return decorator


def handle_unknown() -> str:
    """Handles unknown actions by returning a default message."""
    return UNKNOWN_ACTION_MESSAGE


@register_handler("GREET")
def handle_greet() -> str:
    """Provides a greeting message."""
    return "Hello! How can I assist you today?"


@register_handler("IDENTIFY")
def handle_identify() -> str:
    """Returns the identity of the assistant."""
    return "I am ACE, your personal assistant."


@register_handler("CREATOR")
def handle_creator() -> str:
    """Returns the name of the creator."""
    return "I was created by Illy Shaieb."


@register_handler("GET_TIME")
def handle_get_time() -> str:
    """Provide the current time in a human-readable format."""
    return f"The current time is {datetime.now().strftime('%H:%M')}."


@register_handler("GET_DATE")
def handle_get_date() -> str:
    """Provide the current date in a human-readable format."""
    now = datetime.now()
    day = now.day
    suffix = (
        "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    )
    return f"Today's date is {now.strftime(f'%A {day}{suffix} %B %Y')}."


@register_handler("HELP")
def handle_help() -> str:
    """Provides a brief description of the assistant's capabilities."""
    return "I can assist you with various tasks. Try asking me about the time, date, or anything else!"


@register_handler("JOKE")
def handle_joke() -> str:
    """Retrieves a random joke and returns it in a human-readable format."""
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        response.raise_for_status()
        joke_data = response.json()
        setup = joke_data.get("setup", "")
        punchline = joke_data.get("punchline", "")
        sentence_stop = punchline.endswith((".", "!", "?"))
        if not setup or not punchline:
            return (
                "Sorry, I couldn't fetch a joke right now. The joke format is invalid."
            )
        return f"{setup} — {punchline}" if sentence_stop else f"{setup} — {punchline}."
    except (requests.exceptions.HTTPError, requests.RequestException) as e:
        return f"Sorry, I couldn't fetch a joke right now. Error: {e}"


@register_handler("FLIP_COIN")
def handle_flip_coin() -> str:
    """Simulates a coin flip and returns the result."""
    return random.choice(["Heads", "Tails"])


@register_handler("ROLL_DIE")
def handle_roll_die() -> str:
    """Simulates rolling a six-sided die and returns the result."""
    return str(random.randint(1, 6))


def execute_action(action: str) -> str:
    """Executes the action based on the provided action name."""
    return ACTION_HANDLERS.get(action, handle_unknown)()
