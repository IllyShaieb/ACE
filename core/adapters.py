"""core.adapters: This module defines adapters for the ACE application, providing
a layer of abstraction for different APIs the tools might depend on."""

import sys
from typing import Any, Dict, Optional

import requests
import rich
from rich.markdown import Markdown

from core.protocols import Sender

##################################################################################
#                                  VIEW ADAPTERS                                 #
##################################################################################


class BuiltinIOAdapter:
    """
    The 'Standard' implementation of I/O.

    Simply wraps Python's built-in functions to satisfy the IOAdapter contract.
    """

    def get_input(self, prompt: str) -> str:
        return input(prompt)

    def display_output(self, message: str, sender: Optional[Sender] = None) -> None:
        if sender is None:
            print(message)
        else:
            match sender:
                case Sender.INFO:
                    formatted = message
                case _:
                    formatted = f"{sender.value}: {message}"
            print(formatted)
            print("")

    def start_loading_indicator(self, message: str) -> None:
        return

    def stop_loading_indicator(self) -> None:
        return


class RichIOAdapter:
    """
    An adapter that uses the `rich` library for enhanced terminal output.

    This adapter provides methods to display formatted messages, tables, and
    other rich content in the terminal.
    """

    def __init__(self):
        self.console = rich.console.Console()
        self._loading_indicator = None

    def get_input(self, prompt: str) -> str:
        # 1. Get input
        user_input = self.console.input(prompt)

        # 2. Clear last line
        lines = (len(prompt) + len(user_input)) // self.console.width + 1
        for _ in range(lines):
            sys.stdout.write("\033[F")  # Move cursor up one line
            sys.stdout.write("\033[K")  # Clear the line
            sys.stdout.flush()

        # 3. Send input back to presenter
        self.display_output(user_input, sender=Sender.USER)
        return user_input

    def display_output(self, message: str, sender: Optional[Sender] = None) -> None:
        if sender is None:
            self.console.print(Markdown(message))
        else:
            match sender:
                case Sender.USER:
                    self.console.print(f"[bold cyan]{sender.value}:[/bold cyan]")
                    self.console.print(Markdown(message))
                case Sender.ACE:
                    self.console.print(f"[bold green]{sender.value}:[/bold green]")
                    self.console.print(Markdown(message))
                case Sender.INFO:
                    self.console.print(f"[italic]{message}[/italic]")
                case _:
                    self.console.print(f"{sender.value}:")
                    self.console.print(Markdown(message))

        self.console.print("")

    def start_loading_indicator(self, message: str) -> None:
        self._loading_indicator = self.console.status(message)
        self._loading_indicator.start()

    def stop_loading_indicator(self) -> None:
        if self._loading_indicator:
            self._loading_indicator.stop()


#################################################################################
#                                  SERVICES ADAPTERS                            #
#################################################################################


class RequestsHTTPAdapter:
    """Adapter for making HTTP requests using the 'requests' library."""

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a GET request to the specified URL with optional query parameters.

        Args:
            url (str): The URL to send the GET request to.
            params (Optional[Dict[str, Any]]): Optional query parameters for the GET request.
            headers (Optional[Dict[str, Any]]): Optional headers for the GET request.

        Returns:
            Any: The JSON response from the GET request. May be a dictionary, list etc.
                depending on the API response.

        Raises:
            RuntimeError: If the HTTP request fails or returns an error status code.
        """
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP GET failed: {e}")

    def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a POST request to the specified URL with form data or JSON payload.

        Args:
            url (str): The URL to send the POST request to.
            data (Optional[Any]): Form-encoded data, bytes, or file objects.
            json (Optional[Dict]): JSON-serializable dictionary payload.
            headers (Optional[Dict[str, Any]]): Optional HTTP headers.

        Returns:
            Any: The JSON response from the POST request. May be a dictionary, list etc.
                depending on the API response.

        Raises:
            RuntimeError: If the HTTP request fails or returns an error status code.
        """
        try:
            response = requests.post(url, data=data, json=json, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP POST failed: {e}")
