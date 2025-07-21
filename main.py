"""main.py - The entry point for the ACE program.

This file is used to start the ACE program and interact with the user,
linking together the various components of the program following the
Model-View-Presenter (MVP) architectural pattern.
"""

from datetime import datetime
from core.model import ACEModel
from core.view import ConsoleView


def main():
    """Main function to start the ACE application."""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Initialising ACE")

    # Initialise MVP layers
    model = ACEModel()
    view = ConsoleView()

    # TODO: Implement the presenter layer
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ACE initialised\n")

    # Start the ACE application
    print(" ACE ".center(80, "="))
    print("    Welcome to ACE! Type 'exit' to quit.\n\n")
    while True:
        user_input = view.get_user_input("YOU: ")
        if user_input == "exit":
            break

        response = model(user_input)
        view.display_message("ACE", response)


if __name__ == "__main__":
    main()
