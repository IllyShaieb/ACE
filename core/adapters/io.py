"""core.adapters.io: This module defines I/O adapters for the ACE application, providing
a layer of abstraction for different input/output implementations.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import rich
from rich.markdown import Markdown
from rich.table import Table

from core.protocols import Sender


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

    def get_session_choice(self, sessions: List[Dict[str, Any]]) -> Optional[str]:
        """Displays a formatted table of recent chats and asks the user to choose.

        Args:
            sessions (List[Dict[str, Any]]): A list of recent conversation sessions, where each session is a dictionary
                containing information about the session, such as 'title', 'updated_at', and 'session_id'.

        Returns:
            Optional[str]: The session_id of the selected conversation session, or None if the user chooses to start a new conversation.
        """
        # If there are no sessions, inform the user and return None to start a new chat
        if not sessions:
            self.console.print(
                "[italic cyan]No previous conversations found. Starting a new chat...[/italic cyan]\n"
            )
            return None

        # Display sessions in a rich table
        table = Table(title="Recent Conversations", title_style="bold magenta")
        table.add_column("#", style="cyan", justify="right")
        table.add_column("Title", style="green")
        table.add_column("Last Updated", style="yellow")

        for idx, session in enumerate(sessions, 1):
            table.add_row(
                str(idx), session.get("title", ""), session.get("updated_at", "")
            )

        self.console.print(table)
        self.console.print("[cyan]0[/cyan]: Start a [bold]New Conversation[/bold]")

        # Create a mapping of valid choices to session IDs
        choices = {str(i): s["session_id"] for i, s in enumerate(sessions, 1)}
        choices["0"] = None

        # Prompt the user to select a session until a valid choice is made
        while True:
            choice = (
                self.console.input("\nSelect a conversation (default 0): ").strip()
                or "0"
            )
            if choice in choices:
                if choice != "0":
                    selected = sessions[int(choice) - 1]
                    self.console.print(
                        f"\n[italic green]Resuming: {selected.get('title', '')}[/italic green]\n\n"
                    )
                return choices[choice]
            self.console.print("[red]Invalid selection. Please try again.[/red]")
