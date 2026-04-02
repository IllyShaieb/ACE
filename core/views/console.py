"""core.views.console: This module defines the ConsoleView class, which implements the view layer for a console-based interface,
responsible for displaying information and receiving user input."""

import asyncio
from typing import Callable

from core.adapters.protocols import IOAdapterProtocol
from core.events import ViewEvents
from core.views.protocols import Sender


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

    async def start(self) -> None:
        """Start the view, allowing it to display information and receive user input."""
        while self._running:
            user_input = await asyncio.to_thread(self.io_adapter.get_input, "YOU: ")

            # Check for exit command to stop the view and end the application
            if user_input.strip().lower() == "exit":
                self.stop()
                break

            await self.events.on_user_input.emit(user_input)

    def stop(self) -> None:
        """Stop the view, cleaning up any resources if necessary."""
        self._running = False

    async def show_loading(
        self, message: str, function: Callable, **func_args: dict
    ) -> None:
        """Show a loading indicator with a message while executing a function, then hide it when done.

        Args:
            message (str): The message to display while loading.
            function (Callable): The function to execute while showing the loading indicator.
            func_args (dict): Additional keyword arguments to pass to the function.
        """
        self.io_adapter.start_loading_indicator(message)
        try:
            # Await the function if it's a coroutine, otherwise call it directly
            if callable(function):
                result = function(**func_args)
                if hasattr(result, "__await__"):
                    return await result
                return result
        finally:
            self.io_adapter.stop_loading_indicator()

    def get_user_input(self, prompt: str) -> str:
        """Get input from the user with a given prompt."""
        return self.io_adapter.get_input(prompt)

    def display_message(self, sender: Sender, message: str) -> None:
        """Display a message to the user."""
        self.io_adapter.display_output(message, sender=sender)

    def show_error(self, error_message: str) -> None:
        """Show an error message to the user."""
        self.io_adapter.display_output(f"ERROR: {error_message}")

    def get_session_choice(self, sessions: list) -> str | None:
        """Display a list of recent sessions and prompt the user to select one."""
        return self.io_adapter.get_session_choice(sessions)
