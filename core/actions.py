"""actions.py: Contains the functions for handling actions in the ACE program."""

import os
import random
import warnings
from datetime import datetime
from random import choice
from typing import Callable, Optional

import requests
import spacy
from dotenv import load_dotenv

load_dotenv()

UNKNOWN_ACTION_MESSAGE = "I'm not sure how to do that."
SPACY_NLP = spacy.load("en_core_web_sm")


class ActionHandler:
    """Class representing an action handler.

    This class encapsulates the handler function and whether it requires user input
    and provides a callable interface to invoke the handler.
    """

    def __init__(self, handler: Callable, requires_user_input: bool):
        """Initialises the ActionHandler.

        ### Args
            handler (Callable): The function that handles the action.
            requires_user_input (bool): Whether the action handler requires user input.
        """
        self.handler = handler
        self.requires_user_input = requires_user_input

    def __call__(self, *args, **kwargs):
        """Invoke the handler function with provided arguments."""
        return self.handler(*args, **kwargs)


ACTION_HANDLERS = {}


def register_handler(
    name: str, requires_user_input: bool = False
) -> Callable[[Callable], Callable]:
    """Decorator to register an action handler and add it to the ACTION_HANDLERS
    dictionary. This allows for easy addition of new actions without modifying the
    execute_action function.

    If a handler with the same name already exists, it will be overwritten and a warning
    thrown. This is for the following reasons:
    1. **Flexibility:** Overriding allows for flexible extension and patching, especially
        in tests or plugins.
    2. **Simplicity:** It keeps the registration process straightforward, avoiding the
       need for additional checks or error handling for duplicate names.
    3. **Developer Awareness:** The warning serves as a notification to developers,
       making them aware of potential conflicts in action names.

    ### Args
        name (str): The name of the action to register.
        requires_user_input (bool): Whether the action handler requires user input.

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
        if name in ACTION_HANDLERS:
            warnings.warn(f"Action handler for '{name}' is being overwritten.")
        ACTION_HANDLERS[name] = ActionHandler(func, requires_user_input)
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


@register_handler("GET_WEATHER", requires_user_input=True)
def handle_get_weather(query: str) -> str:
    """Fetches and returns the current weather information."""

    doc = SPACY_NLP(query)
    location = None

    # First, try to find a GPE (Geopolitical Entity)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            location = ent.text
            break

    # If no GPE is found, fall back to finding proper nouns after a preposition
    if not location:
        for token in doc:
            if token.lower_ in ["in", "for"] and token.pos_ == "ADP":
                # Find the noun phrase that follows the preposition
                for child in token.children:
                    if child.pos_ in ("PROPN", "NOUN"):
                        # Reconstruct the full location name from the subtree
                        location_parts = [
                            t.text for t in child.subtree if t.pos_ in ("PROPN", "NOUN")
                        ]
                        if location_parts:
                            location = " ".join(location_parts)
                            break
                if location:
                    break

    if not location:
        return "I'm sorry, I couldn't find a location in your query."

    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Apologies, it appears the WEATHER_API_KEY is not set."

    api_url = "https://api.weatherapi.com/v1/current.json"

    try:
        resp = requests.get(api_url, params={"key": api_key, "q": location}, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        curr = data["current"]
        cond = curr["condition"]

        wording_options = [
            (
                f"The prevailing weather in {data['location']['name']} is {cond['text'].lower()}. "
                f"The temperature is currently {curr['temp_c']}°C, feeling like {curr['feelslike_c']}°C."
            ),
            (
                f"In {data['location']['name']}, the weather is {cond['text'].lower()} and the temperature is {curr['temp_c']}°C, "
                f"which feels like {curr['feelslike_c']}°C."
            ),
            (
                f"It's {cond['text'].lower()} in {data['location']['name']} right now. The temperature is {curr['temp_c']}°C, "
                f"but it feels more like {curr['feelslike_c']}°C."
            ),
            (
                f"The weather report for {data['location']['name']} shows {cond['text'].lower()} with a temperature of {curr['temp_c']}°C. "
                f"The 'feels like' temperature is {curr['feelslike_c']}°C."
            ),
            (
                f"{data['location']['name']} is experiencing {cond['text'].lower()} weather. It's {curr['temp_c']}°C outside, "
                f"and it feels like {curr['feelslike_c']}°C."
            ),
        ]

        return choice(wording_options)

    except requests.exceptions.RequestException as e:  # Handle network/HTTP errors
        return f"Sorry, I couldn't connect to the weather service. Error: {e}"

    except KeyError:  # Handle unexpected JSON structure
        return "Sorry, I received an unexpected response from the weather service."

    except Exception as e:
        return f"Sorry, I couldn't fetch the weather information right now. Error: {e}"


def execute_action(action: str, query: Optional[str] = None) -> str:
    """Executes the action based on the provided action name.

    ### Args
        action (str): The name of the action to execute.
        query (Optional[str]): The user's query, if required by the action.
    """
    handler_obj = ACTION_HANDLERS.get(action)
    if not handler_obj:
        return handle_unknown()

    requires_user_input = handler_obj.requires_user_input

    if requires_user_input:
        if query is None:
            return f"The action '{action}' requires user input."
        return handler_obj(query)
    else:
        return handler_obj()
