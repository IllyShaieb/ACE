"""core.views.protocols: Protocol definitions for the view components of ACE, specifying the expected
interfaces for displaying information and receiving user input."""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable

from core.events import ViewEvents


class Sender(Enum):
    """Enum to represent the sender of a message in the view."""

    USER = "USER"
    ACE = "ACE"
    INFO = "INFO"


@runtime_checkable
class ViewProtocol(Protocol):
    """Protocol for the view component, defining the expected interface for displaying
    information and receiving user input."""

    @property
    def events(self) -> ViewEvents:
        """Return the view's events for user interaction."""
        ...

    async def start(self) -> None:
        """Start the view, allowing it to display information and receive user input."""
        ...

    def stop(self) -> None:
        """Stop the view, cleaning up any resources if necessary."""
        ...

    async def show_loading(
        self, message: str, function: Callable, **func_args: dict
    ) -> None:
        """Show a loading indicator with a message while executing a function, then hide it when done."""
        ...

    def get_user_input(self, prompt: str) -> str:
        """Get input from the user with a given prompt."""
        ...

    def display_message(self, sender: Sender, message: str) -> None:
        """Display a message to the user."""
        ...

    def show_error(self, error_message: str) -> None:
        """Show an error message to the user."""
        ...

    def get_session_choice(self, sessions: List[Dict[str, Any]]) -> Optional[str]:
        """Display a list of recent sessions and prompt the user to select one."""
        ...
