"""main.py - The entry point for the ACE program.

This file is used to start the ACE program and interact with the user,
linking together the various components of the program following the
Model-View-Presenter (MVP) architectural pattern.
"""

from core.model import ACEModel
from core.view import DesktopView, ConsoleView
from core.presenter import DesktopPresenter, ConsolePresenter

# Define available applications with their models, views, and presenters
APPS = {
    "1": ("Desktop Application", ACEModel, DesktopView, DesktopPresenter),
    "2": ("Console Application", ACEModel, ConsoleView, ConsolePresenter),
}


def select_app():
    """Prompt the user to select an application mode."""
    print("Select the application mode:")
    for key, (description, *_) in APPS.items():
        print(f"  {key}. {description}")

    while True:
        choice = input("Enter your choice: ").strip()
        if choice in APPS:
            return choice
        print("Invalid choice. Please try again.")


def main():
    """Main function to start the ACE application."""

    try:
        # Select the application mode
        choice = select_app()
        print(f"Starting {APPS[choice][0]}...")

        # Instantiate selected app
        model = APPS[choice][1]()
        view = APPS[choice][2]()
        presenter = APPS[choice][3](model, view)

        # Start the application
        presenter.run()

    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")


if __name__ == "__main__":
    main()
