"""main.py - The entry point for the ACE program.

This file is used to start the ACE program and interact with the user,
linking together the various components of the program.

To run the program, simply execute this file using `uv`:
    $ uv run main.py

If you haven't installed `uv` yet, you can do so using pip:
    $ pip install uv
"""
from brain import __version__

ACE_ID: str = "ACE"
USER_ID: str = "YOU"
EXIT_COMMAND: str = "exit"

def main():
    print(f" ACE v{__version__} ".center(80, "="), end="\n\n")
    print(f"To exit the program, type '{EXIT_COMMAND}' and press Enter.".center(80, " "), end="\n\n")
    print(f"{ACE_ID}: Hello! I am ACE, how can I help you?")

    while True:
        user_input = input(f"{USER_ID}: ").strip().lower()
        if user_input.lower() == EXIT_COMMAND:
            print(f"{ACE_ID}: Goodbye!")
            break
        else:
            print(f"{ACE_ID}: Sorry, I don't understand that command.")

if __name__ == "__main__":
    main()
