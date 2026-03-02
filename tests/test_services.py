"""tests.test_services: Ensure that services are correctly defined and can be used by tools."""

import unittest
from unittest.mock import MagicMock

from core import services
from core.protocols import HTTPClientAdapterProtocol, WeatherUnits


class TestWeatherService(unittest.TestCase):
    """Test the WeatherService's ability to fetch weather information using an HTTP client adapter."""

    def setUp(self):
        """Set up common test components."""
        self.mock_http_client_adapter = MagicMock(spec=HTTPClientAdapterProtocol)
        self.weather_service = services.OpenWeatherMapService(
            self.mock_http_client_adapter, api_key="test_api_key"
        )

    def test_get_current_weather_success(self):
        """Verify that `get_current_weather()` returns a dictionary with weather information."""
        # ARRANGE: Define the expected weather information and mock the HTTP client's response
        test_cases = [
            {
                "location": "London,GB",
                "units": WeatherUnits.METRIC,
                "expected_response": {
                    "temperature": "20°C",
                    "feels_like": "18°C",
                    "condition": "Cloudy",
                    "wind_speed": "5.2 m/s",
                    "humidity": "60%",
                },
                "description": "Should return weather information in metric units.",
            }
        ]

        for case in test_cases:
            with self.subTest(msg=case["description"]):
                # Mock the HTTP client's response to return the expected weather information
                self.mock_http_client_adapter.get.side_effect = [
                    [{"lat": 51.5073, "lon": -0.1276, "name": "London"}],
                    {
                        "current": {
                            "temp": 20,
                            "feels_like": 18,
                            "humidity": 60,
                            "wind_speed": 5.2,
                            "weather": [{"description": "Cloudy"}],
                        }
                    },
                ]

                # ACT: Call the `get_current_weather()` method with the specified location
                # and units
                result = self.weather_service.get_current_weather(
                    location=case["location"], units=case["units"]
                )

                # ASSERT: Verify that the result matches the expected weather information
                self.assertEqual(result, case["expected_response"])

    def test_get_current_weather_location_not_found(self):
        """Verify the service handles invalid locations gracefully."""
        # ARRANGE: Mock the API returning an empty list for a fake city
        self.mock_http_client_adapter.get.return_value = []

        # ACT & ASSERT: Call the `get_current_weather()` method and expect a RuntimeError
        with self.assertRaises(ValueError):
            self.weather_service.get_current_weather(location="FakeCity,FC")


if __name__ == "__main__":
    unittest.main()
