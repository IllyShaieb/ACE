"""actions.py: Contains the functions for handling actions in the ACE program."""

import os
import random
import warnings
from datetime import datetime
from typing import Callable, Dict

import requests
from dotenv import load_dotenv

load_dotenv()

UNKNOWN_ACTION_MESSAGE = "I'm not sure how to do that."


class ActionHandler:
    """Class representing an action handler.

    This class encapsulates the handler function and whether it requires user input
    and provides a callable interface to invoke the handler.
    """

    def __init__(
        self, handler: Callable, requires_user_input: bool, description: str = ""
    ):
        """Initialises the ActionHandler.

        ### Args
            handler (Callable): The function that handles the action.
            requires_user_input (bool): Whether the action handler requires user input.
            description (str): A brief description of the action.
        """
        self._handler = handler
        self._requires_user_input = requires_user_input
        self._description = description

    @property
    def handler(self) -> Callable:
        """Gets the handler function."""
        return self._handler

    @property
    def requires_user_input(self) -> bool:
        """Gets whether the action handler requires user input."""
        return self._requires_user_input

    @property
    def description(self) -> str:
        """Gets the description of the action."""
        return self._description

    def __call__(self, *args, **kwargs):
        """Invoke the handler function with provided arguments."""
        return self.handler(*args, **kwargs)


ACTION_HANDLERS: Dict[str, ActionHandler] = {}


def register_handler(
    name: str, requires_user_input: bool = False, description: str = ""
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
        description (str): A brief description of the action.

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
            warnings.warn(
                f"Action handler for '{name}' is being overwritten.", UserWarning
            )
        ACTION_HANDLERS[name] = ActionHandler(func, requires_user_input, description)
        return func

    return decorator


def handle_unknown() -> str:
    """Handles unknown actions by returning a default message."""
    return UNKNOWN_ACTION_MESSAGE


@register_handler(
    "IDENTIFY_SELF",
    description="Informs the user about the assistant's name and purpose.",
)
def handle_identify_self() -> str:
    """Returns the identity of the assistant."""
    return "I am ACE, your Artificial Consciousness Engine, dedicated to maximizing your efficiency."


@register_handler(
    "SELF_CREATOR",
    description="Provides information about the assistant's creator.",
)
def handle_self_creator() -> str:
    """Returns the name of the creator."""
    return "My development was overseen by Illy Shaieb."


@register_handler(
    "GET_TIME",
    description="Retrieves the current time of day.",
)
def handle_get_time() -> str:
    """Provide the current time in a human-readable format."""
    return f"The current time is {datetime.now().strftime('%H:%M')}."


@register_handler(
    "GET_DATE",
    description="Retrieves the current date.",
)
def handle_get_date() -> str:
    """Provide the current date in a human-readable format."""
    now = datetime.now()
    day = now.day
    suffix = (
        "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    )
    return f"Today's date is {now.strftime(f'%A {day}{suffix} %B %Y')}."


@register_handler(
    "HELP",
    description="Informs the user about the general range of capabilities the assistant has.",
)
def handle_help() -> str:
    """Provides a brief description of the assistant's capabilities."""

    # We now retrieve the tool descriptions and let the LLM format the final response.
    tool_list = [
        f"- {name}: {handler.description}"
        for name, handler in ACTION_HANDLERS.items()
        if name not in ["GENERAL_ENQUIRY", "HELP"]
    ]
    tool_list_str = "\n".join(tool_list)

    # The LLM will use this structured list to generate a natural, persona-driven response.
    return f"My current programmed capabilities are:\n{tool_list_str}"


@register_handler(
    "JOKE",
    description="Retrieves a random joke.",
)
def handle_joke() -> str:
    """Retrieves a random joke and returns it in a human-readable format."""
    try:
        response = requests.get(
            "https://official-joke-api.appspot.com/random_joke", timeout=5
        )
        response.raise_for_status()
        joke_data = response.json()
        setup = joke_data.get("setup", "")
        punchline = joke_data.get("punchline", "")
        if not setup or not punchline:
            return "I could not retrieve a joke with a valid setup and punchline, Sir."

        return f"{setup}—{punchline}"

    except requests.exceptions.RequestException as e:
        return f"I regret to inform you, Sir, that the joke API is currently unresponsive. Error: {e}"


@register_handler(
    "FLIP_COIN",
    description="Performs a coin toss and reports the result.",
)
def handle_flip_coin() -> str:
    """Simulates a coin flip and returns the result."""
    return random.choice(["Heads", "Tails"])


@register_handler(
    "ROLL_DICE",
    description="Simulates rolling one or more dice and returns the results.",
    requires_user_input=True,
)
def handle_roll_dice(sides: list[int]) -> str:
    """Simulates rolling a die and returns the result.

    ### Args
        sides (list[int]): A list of integers representing the number of sides on each die to roll.
            If not provided, defaults to a single 6-sided die.

    ### Returns
        str: A human-readable string with the results of the dice rolls.
    """
    sides = sides or [6]  # Default to a single 6-sided die if no sides provided

    results = [random.randint(1, side) for side in sides]
    total = sum(results)

    # Group dice by number of sides
    from collections import Counter

    side_counts = Counter(sides)
    if len(sides) == 1:
        return (
            f"You rolled a {sides[0]}-sided die and got: {results[0]}. Total: {total}"
        )
    elif len(side_counts) == 1:
        count = len(sides)
        side = sides[0]
        return f"You rolled {count} {side}-sided dice and got: {', '.join(map(str, results))}. Total: {total}"
    else:
        grouped = [
            f"{count} {side}-sided" if count > 1 else f"{side}-sided"
            for side, count in side_counts.items()
        ]
        return f"You rolled {', '.join(grouped)} dice and got: {', '.join(map(str, results))}. Total: {total}"


@register_handler(
    "GET_WEATHER",
    description="Fetches and returns the current weather for a specified location.",
    requires_user_input=True,
)
def handle_get_weather(location: str) -> str:
    """
    Fetches weather data from an external API and formats it into a human-readable response.
    """
    if not location:
        return "What location would you like to know the weather for?"

    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Apologies, it appears the WEATHER_API_KEY is not set."

    api_url = "https://api.weatherapi.com/v1/current.json"

    try:
        resp = requests.get(api_url, params={"key": api_key, "q": location}, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        # Extract relevant weather details
        try:
            location_name = data["location"]["name"]
            region = data["location"]["region"]
            country = data["location"]["country"]
            temp_c = data["current"]["temp_c"]
            condition = data["current"]["condition"]["text"]
            wind_kph = data["current"]["wind_kph"]
            humidity = data["current"]["humidity"]
            feelslike_c = data["current"]["feelslike_c"]

        except KeyError as e:
            return f"Received unexpected data format from the weather service: {e}"

        # Format the response
        return (
            f"The current weather in {location_name}, {region}, {country} is {temp_c}°C with {condition}. "
            f"The wind speed is {wind_kph} kph, the humidity is {humidity}%, and it feels like {feelslike_c}°C."
        )

    except requests.exceptions.RequestException as e:
        return f"Weather service is unavailable. Connection Error: {e}"

    except Exception as e:
        return f"An unknown issue occurred during the weather retrieval: {e}"


def execute_action(action: str, **kwargs) -> str:
    """Executes the action based on the provided action name and arguments."""
    handler_obj = ACTION_HANDLERS.get(action)
    if not handler_obj:
        return handle_unknown()

    try:
        # Pass all keyword arguments directly to the handler
        return handler_obj.handler(**kwargs)
    except Exception as e:
        return f"System Error during tool execution: {e}"
