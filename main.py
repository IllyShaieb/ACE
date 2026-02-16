"""main.py: Entry point for the ACE application.

Handles the wiring of concrete components via Dependency Injection.
"""

from core.models import MinimumViableModel
from core.presenters import ConsolePresenter
from core.views import BuiltinIOAdapter, ConsoleView

# Configuration
CONFIG = {
    "WELCOME_MESSAGE": """
###############################################################
#           ACE - The Artificial Consciousness Engine         #
###############################################################

I am a simple implementation of an AI assistant, designed to
demonstrate the core architecture of ACE.
    - Type 'exit' to quit the application.
    - Ask me anything or just say hello!
""",
}


def main():
    """Initialize the model, view, and presenter, then run the application."""
    # 1. Create the low-level I/O hardware
    io_adapter = BuiltinIOAdapter()

    # 2. Initialize the Passive View with the adapter
    view = ConsoleView(io_adapter=io_adapter)

    # 3. Initialize the Minimum Viable Model (The Brain)
    model = MinimumViableModel()

    # 4. Inject View and Model into the Presenter (The Switchboard)
    presenter = ConsolePresenter(
        model=model, view=view, welcome_message=CONFIG["WELCOME_MESSAGE"]
    )

    # 5. Execute
    try:
        presenter.run()
    except KeyboardInterrupt:
        print("\nACE safely interrupted. Goodbye!")


if __name__ == "__main__":
    main()
