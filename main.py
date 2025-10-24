"""main.py - The entry point for the ACE program.

This file is used to start the ACE program and interact with the user,
linking together the various components of the program following the
Model-View-Presenter (MVP) architectural pattern.
"""

import os

from dotenv import load_dotenv

from core.model import ACEModel
from core.presenter import ConsolePresenter, DesktopPresenter
from core.view import ConsoleView, DesktopView

# Load environment variables from .env file
load_dotenv()

# Define available applications with their models, views, and presenters
APPS = {
    "1": ("Desktop Application", ACEModel, DesktopView, DesktopPresenter),
    "2": ("Console Application", ACEModel, ConsoleView, ConsolePresenter),
}


def select_app(mode_override: str = "0") -> str:
    """Prompt the user to select an application mode.

    Args:
        mode_override (str): If not "0", this value is used to select the mode directly.

    Returns:
        str: The selected application mode key.
    """
    match mode_override:
        case "0":
            print("Select the application mode:")
            for key, (description, *_) in APPS.items():
                print(f"  {key}. {description}")

            choice = input("Enter your choice: ").strip()
            while choice not in APPS:
                choice = input("Invalid choice. Please try again: ").strip()
            return choice
        case _:
            return mode_override


def main():
    """Main function to start the ACE application."""

    # Check for mode override from environment variable
    mode_override = os.getenv("ACE_MODE_OVERRIDE", "0").strip()
    choice = select_app(mode_override)

    try:
        selected_app = APPS[choice]
        print(f"Starting {selected_app[0]}...")

        # Instantiate selected app
        model_class = selected_app[1]
        view_class = selected_app[2]
        presenter_class = selected_app[3]

        model = model_class()
        view = view_class()
        presenter = presenter_class(model, view)

        # Start the application
        presenter.run()

        # Clean up and exit
        print(f"Exiting {APPS[choice][0]}...")

    except KeyError:
        print(f"Invalid mode override ({mode_override}). Available modes are:")
        for key, (description, *_) in APPS.items():
            print(f"  {key}. {description}")
        return


if __name__ == "__main__":
    main()
