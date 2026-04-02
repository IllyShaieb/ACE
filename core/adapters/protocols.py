"""core.adapters.protocols: This module defines protocols for adapters used in the ACE application, specifying
the expected interfaces for various types of adapters."""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from core.views.protocols import Sender


@runtime_checkable
class IOAdapterProtocol(Protocol):
    """Protocol for input/output adapters, defining the expected interface for
    handling user input and output operations."""

    def get_input(self, prompt: str) -> str:
        """Get input from the user with a given prompt."""
        ...

    def display_output(self, message: str, sender: Optional["Sender"] = None) -> None:
        """Display a message to the user, with optional sender-specific styling."""
        ...

    def start_loading_indicator(self, message: str) -> None:
        """Start a loading indicator with a given message."""
        ...

    def stop_loading_indicator(self) -> None:
        """Stop the loading indicator."""
        ...

    def get_session_choice(self, sessions: List[Dict[str, Any]]) -> Optional[str]:
        """Display a list of recent sessions and prompt the user to select one."""
        ...


@runtime_checkable
class HTTPClientAdapterProtocol(Protocol):
    """Protocol for an HTTP client adapter, defining the expected interface for making
    HTTP requests."""

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a GET request to the specified URL with optional query parameters and headers."""
        ...

    def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a POST request to the specified URL with form data or JSON payload and optional headers."""
        ...


@runtime_checkable
class ConversationStorageAdapterProtocol(Protocol):
    """Protocol for a conversation storage adapter, defining the expected interface for
    storing and retrieving conversation history."""

    def create_session(self, title: Optional[str] = None) -> str:
        """Create a new conversation session and return its unique identifier."""
        ...

    def save_message(self, session_id: str, role: str, content: str) -> None:
        """Save a message to the conversation history for a given session."""
        ...

    def get_session_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieve the conversation history for a given session ID."""
        ...

    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve a list of recent conversation sessions, including session IDs and metadata."""
        ...

    def update_session_title(self, session_id: str, title: str) -> None:
        """Update the title of a conversation session."""
        ...

    def delete_session(self, session_id: str) -> None:
        """Delete a conversation session and its associated messages."""
        ...


class LogStorageAdapterProtocol(Protocol):
    """Protocol for a log storage adapter, defining the expected interface for
    storing and retrieving application logs."""

    def log_event(
        self, level: str, source: str, message: str, details: Optional[str] = None
    ) -> None:
        """Log an event with a given level, source, message, and optional details."""
        ...

    def get_recent_logs(
        self, limit: int = 100, level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve a list of recent log entries, optionally filtered by level."""
        ...

    def delete_logs(
        self, level: Optional[str] = None, source: Optional[str] = None
    ) -> None:
        """Delete log entries, optionally filtered by level and source."""
        ...
