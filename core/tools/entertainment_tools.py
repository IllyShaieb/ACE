"""core.tools.entertainment_tools: This module provides tools for entertainment-related
functionalities.
"""

import random

import requests

from core.tools import TOOL_HANDLERS, register_tool


@register_tool(
    name="TELL_JOKE",
    description="Tells a random joke to entertain the user.",
    registry=TOOL_HANDLERS,
)
def tell_joke() -> str:
    """Fetch and return a random joke from an external API."""
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        response.raise_for_status()
        joke_data = response.json()

        return f"{joke_data['setup']}—{joke_data['punchline']}"
    except requests.RequestException as e:
        return f"Sorry, I couldn't fetch a joke at this time: {e.__class__.__name__} - {e}."
    except KeyError:
        return "Sorry, I couldn't understand the joke data received."


@register_tool(
    name="FLIP_COIN",
    description="Simulates a coin flip and returns the result.",
    registry=TOOL_HANDLERS,
)
def flip_coin() -> str:
    """Simulates a coin flip and returns the result."""
    return random.choice(["Heads", "Tails"])


@register_tool(
    name="ROLL_DICE",
    description="Simulates rolling one or more dice and returns the results.",
    registry=TOOL_HANDLERS,
)
def roll_dice(sides: list[int]) -> str:
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
        return f"You rolled the following dice: {', '.join(grouped)} and got: {', '.join(map(str, results))}. Total: {total}"
