import re

from ace import skills_dict


def get_user_input() -> str:
    """Get user input."""
    return input("User: ")


def process_user_input(user_input: str) -> str:
    """Process user input."""
    processed_input = user_input.lower()
    processed_input = re.sub(r"[^\w\s]", "", processed_input)

    return processed_input


def recognise_intent(processed_input: str) -> str:
    """Recognise intent."""
    if processed_input == "run dummy skill":
        return "DUMMY_SKILL"


def extract_entities(processed_input: str) -> list[tuple[str, str]]:
    """Extract entities."""
    return []


def select_skill(intent: str) -> callable:
    """Select skill function based on intent."""
    return skills_dict[intent]
