"""core.presenters.protocols: Protocol definitions for the presenter components of ACE, specifying the
expected interfaces for mediating between the model and view."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class PresenterProtocol(Protocol):
    """Protocol for the presenter component, defining the expected interface for
    mediating between the model and view."""

    async def run(self) -> None:
        """Run the presenter, starting the main application loop."""
        ...

    async def handle_user_input(self, user_input: str) -> None:
        """Handle user input, process it through the model, and update the view."""
        ...
