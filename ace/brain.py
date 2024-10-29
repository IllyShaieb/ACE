import re


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
    if processed_input == "this is a dummy user input":
        return "DUMMY"


def select_skill(intent: str) -> str:
    """Select skill."""
    if intent == "DUMMY":
        return "DUMMY_SKILL"
    else:
        return "UNKNOWN_SKILL"
