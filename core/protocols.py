"""core.protocols: This module defines protocols for the ACE application, specifying
the expected interfaces for various components."""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable

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

    def load_session(self, session_id: Optional[str] = None) -> None:
        """Load a conversation session by ID, or start a new session if no ID is provided."""
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


#######################################################################################
#                                 PRESENTER PROTOCOLS                                 #
#######################################################################################


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


#######################################################################################
#                                   TOOL PROTOCOLS                                    #
#######################################################################################


@runtime_checkable
class ToolProtocol(Protocol):
    """Protocol for tools, defining the expected interface for functional tools that
    ACE can use."""

    @property
    def name(self) -> str:
        """Return the name of the tool."""
        ...

    @property
    def description(self) -> str:
        """Return a brief description of the tool's functionality."""
        ...

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return a schema defining the parameters required by the tool."""
        ...

    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool's functionality with the given parameters."""
        ...


###########################################################################################
#                                SERVICES PROTOCOLS                                       #
###########################################################################################
class WeatherUnits(Enum):
    """Enum to represent units of measurement for weather information."""

    STANDARD = "standard"
    METRIC = "metric"
    IMPERIAL = "imperial"


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
class WeatherServiceProtocol(Protocol):
    """Protocol for a weather service, defining the expected interface for fetching
    weather information."""

    def get_current_weather(
        self, location: str, units: WeatherUnits = WeatherUnits.STANDARD
    ) -> Dict[str, str]:
        """Get the current weather for a given location."""
        ...

    def get_future_weather(
        self,
        location: str,
        units: WeatherUnits = WeatherUnits.STANDARD,
        forecast_type: str = "daily",
    ) -> Dict[str, str]:
        """Get the future weather for a given location.

        Args:
            forecast_type: 'daily' for the next 5 days, 'hourly' for the next 12 hours.
        """
        ...


@runtime_checkable
class LocationServiceProtocol(Protocol):
    """Protocol for a location service, defining the expected interface for fetching
    location information."""

    def get_location(self) -> Dict[str, str]:
        """Get the location information based on the client's IP address."""
        ...


###########################################################################################
#                                  STORAGE PROTOCOLS                                      #
###########################################################################################


@runtime_checkable
class DatabaseServiceProtocol(Protocol):
    """Protocol for a generic database service, providing standard low-level DB operations.

    Uses CRUD-like methods for executing SQL queries and managing transactions, abstracting
    away the underlying database implementation details.
    """

    def create_table(self, configuration: Dict[str, Any]) -> None:
        """Create a table in the database based on the provided configuration."""
        ...

    def delete_table(self, table_name: str) -> None:
        """Delete an existing table by name."""
        ...

    def insert(
        self,
        table: str,
        data: Dict[str, Any],
    ) -> None:
        """Inserts new data into a database"""
        ...

    def select(
        self,
        table: str,
        headers: Optional[List[str]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        distinct: bool = False,
    ) -> List:
        """Extracts data from a database"""
        ...

    def update(
        self,
        table: str,
        updates: Dict[str, Any],
        conditions: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Updates data in a database"""
        ...

    def delete(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> None:
        """Deletes data from a database"""
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
