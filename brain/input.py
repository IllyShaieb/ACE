"""input.py: Handles various input methods for the ACE program.

This module contains methods to handle input from the user, and
provides methods for validating and processing the input.

functions:
- text_input: Handles text input from the user.
"""

def text_input(prompt: str) -> str:
    """Handles text input from the user.

    Args:
        prompt (str): The prompt to display to the user.

    Returns:
        str: The user's input as a string, with the leading and trailing
             whitespace removed.
    """
    while True:
        response = input(prompt).strip()
        if response:
            return response
        else:
            print(f"{prompt}Hmmm, how can I help you if you don't say anything?")
