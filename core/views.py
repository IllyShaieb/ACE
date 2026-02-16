"""core.views: This module defines the view classes for the ACE application, responsible for displaying
information and receiving user input."""

from typing import Callable

from core.events import ViewEvents
from core.protocols import IOAdapterProtocol, Sender


class BuiltinIOAdapter:
    """
    The 'Standard' implementation of I/O.

    Simply wraps Python's built-in functions to satisfy the IOAdapter contract.
    """

    def get_input(self, prompt: str) -> str:
        return input(prompt)

    def display_output(self, message: str) -> None:
        print(message)

    def start_loading_indicator(self, message: str) -> None:
        return

    def stop_loading_indicator(self) -> None:
        return


class ConsoleView:
    """View for the console-based interface, responsible for displaying information
    and receiving user input."""

    def __init__(self, io_adapter: IOAdapterProtocol):
        """Initialise the view with the given IO adapter.

        Args:
            io_adapter (IOAdapterProtocol): The IO adapter to use for input/output operations.
        """
        self.io_adapter = io_adapter
        self._events = ViewEvents()
        self._running = True  # Flag to control the main loop in start()

    @property
    def events(self) -> ViewEvents:
        """Return the view's persistent events instance."""
        return self._events

    def start(self) -> None:
        """Start the view, allowing it to display information and receive user input."""
        while self._running:
            user_input = self.io_adapter.get_input("YOU: ")

            # Check for exit command to stop the view and end the application
            if user_input.strip().lower() == "exit":
                self.stop()
                break

            self.events.on_user_input.emit(user_input)

    def stop(self) -> None:
        """Stop the view, cleaning up any resources if necessary."""
        self._running = False

    def show_loading(self, message: str, function: Callable, **func_args: dict) -> None:
        """Show a loading indicator with a message while executing a function, then hide it when done.

        Args:
            message (str): The message to display while loading.
            function (Callable): The function to execute while showing the loading indicator.
            func_args (dict): Additional keyword arguments to pass to the function.
        """
        self.io_adapter.start_loading_indicator(message)
        function(**func_args)
        self.io_adapter.stop_loading_indicator()

    def get_user_input(self, prompt: str) -> str:
        """Get input from the user with a given prompt."""
        return self.io_adapter.get_input(prompt)

    def display_message(self, sender: Sender, message: str) -> None:
        """Display a message to the user."""
        match sender:
            case Sender.INFO:
                formatted_message = message
            case _:
                formatted_message = f"{sender.value}: {message}"

        self.io_adapter.display_output(formatted_message)

    def show_error(self, error_message: str) -> None:
        """Show an error message to the user."""
        self.io_adapter.display_output(f"ERROR: {error_message}")
