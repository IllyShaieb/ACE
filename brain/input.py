"""input.py: Handles various input methods for the ACE program.

This module contains methods to handle input from the user, and
provides methods for validating and processing the input.

functions:
- text_input: Handles text input from the user.
"""


class InvalidInputError(Exception):
    """An exception raised when the user provides invalid input."""

    ...


def text_input(prompt: str) -> str:
    """Handles text input from the user.

    Args:
        prompt (str): The prompt to display to the user.

    Returns:
        str: The user's input as a string, with the leading and trailing
             whitespace removed.

    Raises:
        InvalidInputError: If the user provides invalid input, such as if
                           the input is empty.
    """
    while True:
        response = input(prompt).strip()
        if response:
            return response
        else:
            raise InvalidInputError(
                "Invalid input: Please provide a non-empty response."
            )
