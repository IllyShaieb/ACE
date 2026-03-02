""" "core.services: This module defines services for the tools, creating a layer of
abstraction for different APIs the tools might depend on."""

from typing import Dict

from core.protocols import HTTPClientAdapterProtocol, WeatherUnits


class OpenWeatherMapService:
    """Service for fetching weather information from the OpenWeatherMap API."""

    def __init__(self, http_client_adapter: HTTPClientAdapterProtocol, api_key: str):
        """Initialize the OpenWeatherMapService with an HTTP client adapter and API key.

        Args:
            http_client_adapter (HTTPClientAdapterProtocol): An adapter for making HTTP requests.
            api_key (str): The API key for accessing the OpenWeatherMap API.
        """
        self.http_client_adapter = http_client_adapter
        self.api_key = api_key
        self.geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.weather_url = "https://api.openweathermap.org/data/3.0/onecall"

    def get_current_weather(
        self, location: str, units: WeatherUnits = WeatherUnits.STANDARD
    ) -> Dict[str, str]:
        """Get the current weather for a given location.

        Args:
            location (str): The location to fetch weather information for, formatted as
                "{city name},{state code},{country code}" using ISO 3166 country codes.
                The state code is only required for US locations.
                Examples: "London,GB", "New York,NY,US", "Paris,FR".
            units (WeatherUnits): The unit system to use for the weather information.
                Defaults to WeatherUnits.STANDARD.
        Returns:
            Dict[str, str]: The current weather information for the specified location.
        """
        # 1. Get the unit symbols based on the specified units
        unit_symbols = {
            WeatherUnits.METRIC: {"temperature": "°C", "wind_speed": "m/s"},
            WeatherUnits.IMPERIAL: {"temperature": "°F", "wind_speed": "mph"},
            WeatherUnits.STANDARD: {"temperature": "K", "wind_speed": "m/s"},
        }
        symbols = unit_symbols[units or WeatherUnits.STANDARD]

        # 1. Handle the Network Call
        try:
            geo_params = {"q": location, "limit": 1, "appid": self.api_key}
            geo_response = self.http_client_adapter.get(self.geo_url, params=geo_params)
        except RuntimeError as e:
            raise RuntimeError(f"Weather API connection failed: {e}")

        # 2. Handle the Business Logic Validation
        if not geo_response:
            raise ValueError(f"Could not find location: {location}")

        lat = geo_response[0]["lat"]
        lon = geo_response[0]["lon"]

        weather_params = {
            "lat": lat,
            "lon": lon,
            "units": units.value if units else WeatherUnits.STANDARD.value,
            "appid": self.api_key,
            "exclude": "minutely,hourly,daily,alerts",
        }

        try:
            weather_response = self.http_client_adapter.get(
                self.weather_url, params=weather_params
            )
        except RuntimeError as e:
            raise RuntimeError(f"Failed to fetch weather data: {e}")

        current_weather = weather_response.get("current", {})
        return {
            "temperature": f"{current_weather.get('temp', 'N/A')}{symbols['temperature']}",
            "feels_like": f"{current_weather.get('feels_like', 'N/A')}{symbols['temperature']}",
            "condition": current_weather.get("weather", [{}])[0].get(
                "description", "N/A"
            ),
            "wind_speed": f"{current_weather.get('wind_speed', 'N/A')} {symbols['wind_speed']}",
            "humidity": f"{current_weather.get('humidity', 'N/A')}%",
        }
