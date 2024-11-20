"""
This module contains the core logic for the ACE digital assistant.

It handles the main processing loop, including:
- Getting user input
- Processing the input
- Recognizing the intent
- Extracting entities
- Selecting and executing the appropriate skill

This module acts as the central coordinator for ACE's actions,
orchestrating the interaction between the user and the various skills.
"""

import re

from ace import skills_dict
from ace.config import INTENT_PATTERNS


def get_user_input() -> str:
    """Gets user input.

    This function gets the user input from various sources.

    Currently, it is only implemented to get input from the console.

    TODO: Implement other sources of input (e.g., GUI, voice input).

    Returns:
        A string containing the user input.
    """
    return input("User: ")


def process_user_input(user_input: str) -> str:
    """Standardises user input for passing through the system.

    This function performs basic preprocessing on the user input, including:
    - Converting the input to lowercase
    - Removing punctuation (except periods, commas, and hyphens)

    Args:
        user_input: A string containing the user input.

    Returns:
        A string containing the processed user input.
    """
    # Convert to lowercase and remove unwanted characters
    processed_input = user_input.lower()
    processed_input = re.sub(r"[^\w\s\.,-]", "", processed_input)

    return processed_input


def recognise_intent(processed_input: str) -> str:
    """Recognises intent based on processed input.

    This function matches the processed input against the intent patterns
    defined in the `INTENT_PATTERNS` dictionary.

    Args:
        processed_input: A string containing the processed user input.

    Returns:
        A string containing the recognised intent, or `None` if no intent
        is recognised.
    """
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, processed_input):
                return intent
    return None


def extract_entities(processed_input: str, intent: str) -> dict:
    """Extracts entities from processed input based on intent.

    This function extracts entities from the processed input based on the
    recognised intent. An entity is a piece of information that the skill
    needs to perform its task.

    Args:
        processed_input: A string containing the processed user input.
        intent: A string containing the recognised intent.

    Returns:
        A dictionary containing the entity name as the key and the entity
        value as the value.
    """
    entities = {}
    if intent in INTENT_PATTERNS:
        for pattern in INTENT_PATTERNS[intent]:
            match = re.search(pattern, processed_input)
            if match:
                # Use groupdict to capture named groups,
                # but also handle unnamed groups for backward compatibility
                entities = match.groupdict()
                if len(entities) < len(match.groups()):
                    for i, value in enumerate(match.groups()):
                        if i + 1 not in entities:
                            entities[i + 1] = value
                break
    return entities


def select_skill(intent: str) -> callable:
    """Selects the appropriate skill function based on the intent.

    This function selects the appropriate skill function based on the intent
    recognised from the user input. The skill function is then returned
    for execution.

    Args:
        intent: A string containing the recognised intent.

    Returns:
        A callable function representing the skill to be executed
        based on the intent.
    """
    return skills_dict[intent]
