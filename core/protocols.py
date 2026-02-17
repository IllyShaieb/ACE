"""core.protocols: This module defines protocols for the ACE application, specifying
the expected interfaces for various components."""

from enum import Enum
from typing import Callable, Protocol, runtime_checkable

from core.events import ViewEvents

######################################################################################
#                                  MODEL PROTOCOLS                                   #
######################################################################################


@runtime_checkable
class ModelProtocol(Protocol):
    """Protocol for the model component, defining the expected interface for data
    management and business logic."""

    async def process_query(self, query: str) -> str:
        """Process a user query asynchronously and return a response."""
        ...


#######################################################################################
#                                   VIEW PROTOCOLS                                    #
#######################################################################################
class Sender(Enum):
    """Enum to represent the sender of a message in the view."""

    USER = "USER"
    ACE = "ACE"
    INFO = "INFO"


@runtime_checkable
class IOAdapterProtocol(Protocol):
    """Protocol for input/output adapters, defining the expected interface for
    handling user input and output operations."""

    def get_input(self, prompt: str) -> str:
        """Get input from the user with a given prompt."""
        ...

    def display_output(self, message: str) -> None:
        """Display a message to the user."""
        ...

    def start_loading_indicator(self, message: str) -> None:
        """Start a loading indicator with a given message."""
        ...

    def stop_loading_indicator(self) -> None:
        """Stop the loading indicator."""
        ...


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

    def show_loading(self, message: str, function: Callable, **func_args: dict) -> None:
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


#######################################################################################
#                                 PRESENTER PROTOCOLS                                 #
#######################################################################################


@runtime_checkable
class PresenterProtocol(Protocol):
    """Protocol for the presenter component, defining the expected interface for
    mediating between the model and view."""

    def run(self) -> None:
        """Run the presenter, starting the main application loop."""
        ...

    async def handle_user_input(self, user_input: str) -> None:
        """Handle user input, process it through the model, and update the view."""
        ...
