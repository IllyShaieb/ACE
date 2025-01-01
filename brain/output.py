"""output.py: Handles various output methods for the ACE program.

This module contains methods to handle output to the user, and provides
methods for formatting and displaying information.

functions:
- text_output: Handles text output to the user.
"""

def text_output(message: str, line_end: str = None) -> None:
    """Handles text output to the user.

    Args:
        message (str): The message to display to the user.
        line_end (str): The line ending character(s) to use. Defaults to None.
    """
    print(message, end=line_end)