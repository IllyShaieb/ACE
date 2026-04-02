"""core.services.protocols: Protocol definitions for the service components of ACE, specifying the expected
interfaces for various services used by the application."""

from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


class WeatherUnits(Enum):
    """Enum to represent units of measurement for weather information."""

    STANDARD = "standard"
    METRIC = "metric"
    IMPERIAL = "imperial"


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
class LocationServiceProtocol(Protocol):
    """Protocol for a location service, defining the expected interface for fetching
    location information."""

    def get_location(self) -> Dict[str, str]:
        """Get the location information based on the client's IP address."""
        ...


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
    ) -> List[Dict[str, Any]]:
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
