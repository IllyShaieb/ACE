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


def select_app(gui_override: bool = False) -> str:
    """Prompt the user to select an application mode."""
    if gui_override:
        return "1"  # Force Desktop Application

    print("Select the application mode:")
    for key, (description, *_) in APPS.items():
        print(f"  {key}. {description}")

    choice = input("Enter your choice: ").strip()
    while choice not in APPS:
        choice = input("Invalid choice. Please try again: ").strip()
    return choice


def main():
    """Main function to start the ACE application."""

    # Check for GUI override from environment variable
    GUI_OVERRIDE = os.getenv("ACE_GUI_OVERRIDE", "false").lower() == "true"

    try:
        # Select the application mode
        choice = select_app(GUI_OVERRIDE)
        print(f"Starting {APPS[choice][0]}...")

        # Instantiate selected app
        model = APPS[choice][1]()
        view = APPS[choice][2]()
        presenter = APPS[choice][3](model, view)

        # Start the application
        presenter.run()

        # Clean up and exit
        print(f"Exiting {APPS[choice][0]}...")

    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")


if __name__ == "__main__":
    main()
