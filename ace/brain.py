import re

from ace import skills_dict
from ace.config import INTENT_PATTERNS


def get_user_input() -> str:
    """Get user input."""
    return input("User: ")


def process_user_input(user_input: str) -> str:
    """Process user input."""
    processed_input = user_input.lower()
    processed_input = re.sub(r"[^\w\s\.,-]", "", processed_input)

    return processed_input


def recognise_intent(processed_input: str) -> str:
    """Recognise intent."""
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, processed_input):
                return intent
    return None


def extract_entities(processed_input: str, intent: str) -> dict:
    """Extract entities from processed input based on intent."""
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
    """Select skill function based on intent."""
    return skills_dict[intent]
