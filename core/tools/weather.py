"""core.tools.weather: Tools for interacting with weather services."""

import os
from typing import Any, Dict, Optional

from core.protocols import LocationServiceProtocol, WeatherServiceProtocol, WeatherUnits


class WeatherTool:
    """A tool that provides the current weather for a specified location."""

    def __init__(
        self,
        weather_service: WeatherServiceProtocol,
        location_service: LocationServiceProtocol,
    ):
        """Initialize the WeatherTool with a weather service.

        Args:
            weather_service (WeatherServiceProtocol): An instance of a weather service that
                can fetch current weather information for a given location.
            location_service (LocationServiceProtocol): An instance of a location service that
                can fetch location information based on the client's IP address.
        """
        self.weather_service = weather_service
        self.location_service = location_service

    @property
    def name(self) -> str:
        """Return the name of the tool."""
        return "get_weather"

    @property
    def description(self) -> str:
        """Return a brief description of the tool's functionality."""
        return "Provides the current, future (daily), or hourly weather for a specified location."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return a schema defining the parameters required by the tool."""
        return {
            "type": "OBJECT",
            "properties": {
                "location": {
                    "type": "STRING",
                    "description": (
                        "The location to get the weather for, formatted as "
                        "'{city name},{state code},{country code}' using ISO 3166 country codes. "
                        "The state code is only required for US locations. "
                        "Examples: 'London,GB', 'New York,NY,US', 'Paris,FR', 'Tokyo'. "
                        "This is optional; if omitted, the tool will automatically determine the location based on the client's IP address."
                    ),
                },
                "units": {
                    "type": "STRING",
                    "description": "The units for the weather data. Can be 'metric', 'imperial' or 'standard'. Defaults to 'metric'.",
                    "enum": ["metric", "imperial", "standard"],
                },
                "forecast_type": {
                    "type": "STRING",
                    "description": "The type of weather forecast to retrieve. Can be 'current' for the current conditions, 'minutely' for the next 1 hour, 'daily' for the next 8 days, or 'hourly' for a hour-by-hour breakdown over the next 48 hours. Defaults to 'current'.",
                    "enum": ["current", "minutely", "daily", "hourly"],
                },
            },
            "required": [],
        }

    def execute(
        self,
        location: Optional[str] = None,
        units: str = "metric",
        forecast_type: str = "current",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get the current or future weather for a specified location.

        Args:
            location (Optional[str]): The location to get the weather for, formatted as
                "{city name},{state code},{country code}" using ISO 3166 country codes.
                The state code is only required for US locations.
                Examples: "London,GB", "New York,NY,US", "Paris,FR".
                If omitted, the tool will automatically determine the location based on the client's IP address.
            units (str): The units for the weather data. Can be 'metric', 'imperial' or
                'standard'. Defaults to 'metric'.
            forecast_type (str): The type of weather forecast to retrieve. Can be 'current',
                'minutely' (next 1 hour), 'daily' (8-day daily summary), or 'hourly' (next 48 hours).
                Defaults to 'current'.

        Returns:
            Dict[str, Any]: A dictionary containing the weather information for the specified location.
        """
        # Map the LLM's string to your Enum
        unit_enum = {
            "metric": WeatherUnits.METRIC,
            "imperial": WeatherUnits.IMPERIAL,
            "standard": WeatherUnits.STANDARD,
        }.get(units.lower(), WeatherUnits.STANDARD)

        # Location is optional, default to environment variable or system's local timezone
        default_location = os.getenv("DEFAULT_LOCATION")

        # If no location is provided, try to determine it from the client's IP address using the location service.
        if not location and not default_location:
            try:
                ipinfo_location = self.location_service.get_location()
                country = ipinfo_location.get("country")
                region = ipinfo_location.get("region")

                match (bool(country), bool(region)):
                    case (True, True):
                        location = f"{region},{country}"
                    case (True, False):
                        location = country
                    case (False, True):
                        location = region

            except Exception as e:
                return {"error": f"Failed to determine location from IP: {e}"}

        location = location or default_location

        if not location:
            return {
                "error": "No location provided and unable to determine location from IP."
            }

        match forecast_type.lower():
            case "minutely":
                weather_data = self.weather_service.get_future_weather(
                    location, unit_enum, forecast_type="minutely"
                )
            case "daily":
                weather_data = self.weather_service.get_future_weather(
                    location, unit_enum, forecast_type="daily"
                )
            case "hourly":
                weather_data = self.weather_service.get_future_weather(
                    location, unit_enum, forecast_type="hourly"
                )
            case _:
                weather_data = self.weather_service.get_current_weather(
                    location, unit_enum
                )

        return {"location": location, "weather": weather_data}
