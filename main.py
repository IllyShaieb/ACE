"""main.py - The entry point for the ACE program.

This file is used to start the ACE program and interact with the user,
linking together the various components of the program.

To run the program, simply execute this file using `uv`:
    $ uv run main.py

If you haven't installed `uv` yet, you can do so using pip:
    $ pip install uv
"""

from brain import __version__
from brain.input import text_input, InvalidInputError
from brain.output import text_output
from brain.models import ACEModel

ACE_ID: str = "ACE"
USER_ID: str = "YOU"
EXIT_COMMAND: str = "exit"


def main():
    """The main entry point for the ACE program.

    This function connects the user input and program output with the
    various models, providing a simple conversational interface for the
    user to interact with the ACE program.
    """
    text_output(f" ACE v{__version__} ".center(80, "="), line_end="\n\n")
    ace_model = ACEModel()
    text_output(f"Type '{EXIT_COMMAND}' to exit.".center(80, " "), "\n\n")
    text_output(f"{ACE_ID}: Hello! I am ACE, how can I help you?")

    while True:

        try:
            user_input = text_input(f"{USER_ID}: ")

            if user_input.lower() == EXIT_COMMAND:
                text_output(f"{ACE_ID}: Goodbye!")
                break

            response = ace_model.query(user_input)
            text_output(f"{ACE_ID}: {response}")

        except InvalidInputError:
            text_output(f"{ACE_ID}: I'm ready. What's on your mind?")
            continue


if __name__ == "__main__":
    main()
