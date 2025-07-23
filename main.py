"""main.py - The entry point for the ACE program.

This file is used to start the ACE program and interact with the user,
linking together the various components of the program following the
Model-View-Presenter (MVP) architectural pattern.
"""

from core.model import ACEModel
from core.view import ConsoleView
from core.presenter import ACEPresenter


def main():
    """Main function to start the ACE application."""
    try:
        # Initialise MVP layers
        model = ACEModel()
        view = ConsoleView()
        presenter = ACEPresenter(model, view)

        # Start the application
        presenter.run()

    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")


if __name__ == "__main__":
    main()
