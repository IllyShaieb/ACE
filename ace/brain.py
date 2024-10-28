import re


def get_user_input() -> str:
    """Get user input."""
    return input("User: ")


def process_user_input(user_input: str) -> str:
    """Process user input."""
    processed_input = user_input.lower()
    processed_input = re.sub(r"[^\w\s]", "", processed_input)

    return processed_input
