"""core.adapters: This module defines adapters for the ACE application, providing
a layer of abstraction for different APIs the tools might depend on."""

import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import rich
from rich.markdown import Markdown

from core.protocols import DatabaseServiceProtocol, Sender

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


#################################################################################
#                                  STORAGE ADAPTERS                             #
#################################################################################


class DatabaseConversationStorageAdapter:
    """Adapter for storing conversation history in a database using a provided database service."""

    def __init__(self, database_service: DatabaseServiceProtocol):
        """Initialize the adapter with a database service that implements the DatabaseServiceProtocol.

        Args:
            database_service (DatabaseServiceProtocol): An instance of a database service that provides
                methods for creating tables, inserting data, updating data, and querying data.
        """
        self.database_service = database_service

        # Initialise the database and create necessary tables
        self.database_service.create_table(
            {
                "table_name": "sessions",
                "columns": {
                    "session_id": "TEXT PRIMARY KEY",
                    "title": "TEXT",
                    "created_at": "TIMESTAMP",
                    "updated_at": "TIMESTAMP",
                },
            }
        )
        self.database_service.create_table(
            {
                "table_name": "messages",
                "columns": {
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "session_id": "TEXT",
                    "timestamp": "TIMESTAMP",
                    "sender": "TEXT",
                    "content": "TEXT",
                },
            }
        )

    def create_session(self, title: Optional[str] = None) -> str:
        """Create a new conversation session and return its unique identifier.

        Args:
            title (Optional[str]): An optional title for the conversation session. If not provided,
                a default title will be used.

        Returns:
            str: The unique identifier (session_id) of the newly created conversation session.
        """
        # Get current timestamp for created_at and updated_at fields
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create session id
        session_id = str(uuid.uuid4())

        # Call the database service to insert a new row
        self.database_service.insert(
            table="sessions",
            data={
                "session_id": session_id,
                "title": title or "New Conversation",
                "created_at": current_timestamp,
                "updated_at": current_timestamp,
            },
        )
        return session_id

    def save_message(self, session_id: str, role: str, content: str) -> None:
        """Save a message to the conversation history for a given session.

        Args:
            session_id (str): The unique identifier of the conversation session to save the message under.
            role (str): The role of the message sender (e.g., "user", "assistant").
            content (str): The content of the message to be saved.
        """
        # Get current timestamp for the message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Call the database service to insert a new message row
        self.database_service.insert(
            table="messages",
            data={
                "session_id": session_id,
                "timestamp": timestamp,
                "sender": role,
                "content": content,
            },
        )

        # Update the session's updated_at timestamp
        self.database_service.update(
            table="sessions",
            updates={"updated_at": timestamp},
            conditions={"session_id": session_id},
        )

    def get_session_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieve the conversation history for a given session ID.

        Args:
            session_id (str): The unique identifier of the conversation session to retrieve messages for.

        Returns:
            List[Dict[str, str]]: A list of messages in the conversation session, each represented as a dictionary
                with keys "timestamp", "sender", and "content".
        """
        # Query the database service to get all messages for the given session_id, ordered by timestamp
        messages = self.database_service.select(
            table="messages",
            headers=["session_id", "timestamp", "sender", "content"],
            conditions={"session_id": session_id},
        )

        # Loop over the messages and convert to a list of dictionaries
        message_list = []
        for message in messages:
            message_list.append(
                {
                    "session_id": message["session_id"],
                    "timestamp": message["timestamp"],
                    "sender": message["sender"],
                    "content": message["content"],
                }
            )
        return sorted(message_list, key=lambda x: x["timestamp"])

    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve a list of recent conversation sessions, including session IDs and metadata."""
        # Standardise limit value: set min to 1
        # limit = max(1, limit)

        # Query the database service to get recent sessions ordered by updated_at timestamp
        sessions = self.database_service.select(
            table="sessions",
            headers=["session_id", "title", "created_at", "updated_at"],
        )

        # Loop over the sessions and convert to a list of dictionaries
        session_list = []
        for session in sessions:
            session_list.append(
                {
                    "session_id": session["session_id"],
                    "title": session["title"],
                    "created_at": session["created_at"],
                    "updated_at": session["updated_at"],
                }
            )
        # Sort sessions by updated_at timestamp in descending order and return the list
        sorted_sessions = sorted(
            session_list, key=lambda x: x["updated_at"], reverse=True
        )

        if limit is not None and limit > 0:
            return sorted_sessions[:limit]
        return sorted_sessions

    def update_session_title(self, session_id: str, title: str) -> None:
        """Update the title of a conversation session."""
        # Check if title is empty or None, and set to default if so
        title = title if title else "New Conversation"

        # Update the session's title and updated_at timestamp
        self.database_service.update(
            table="sessions",
            updates={
                "title": title,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            conditions={"session_id": session_id},
        )

    def delete_session(self, session_id: str) -> None:
        """Delete a conversation session and its associated messages."""
        # Delete all messages associated with the session
        self.database_service.delete(
            table="messages", conditions={"session_id": session_id}
        )

        # Delete the session itself
        self.database_service.delete(
            table="sessions", conditions={"session_id": session_id}
        )
