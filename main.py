"""main.py - The entry point for the ACE program.

This file is used to start the ACE program and interact with the user,
linking together the various components of the program.

To run the program, simply execute this file using `uv`:
    $ uv run main.py

If you haven't installed `uv` yet, you can do so using pip:
    $ pip install uv
"""
from brain import __version__
from brain.input import text_input
from brain.output import text_output

ACE_ID: str = "ACE"
USER_ID: str = "YOU"
EXIT_COMMAND: str = "exit"

def main():
    text_output(f" ACE v{__version__} ".center(80, "="), line_end="\n\n")
    text_output(f"To exit the program, type '{EXIT_COMMAND}' and press Enter.".center(80, " "), line_end="\n\n")
    text_output(f"{ACE_ID}: Hello! I am ACE, how can I help you?")

    while True:
        user_input = text_input(f"{USER_ID}: ")
        if user_input.lower() == EXIT_COMMAND:
            text_output(f"{ACE_ID}: Goodbye!")
            break
        else:
            text_output(f"{ACE_ID}: Sorry, I don't understand.")

if __name__ == "__main__":
    main()
