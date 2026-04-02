"""tests.tools.test_weather: Ensure that the WeatherTool functions correctly, returning expected weather
information based on mocked service responses."""

import unittest
from unittest.mock import Mock, patch

from core import protocols
from core.tools import weather


class TestWeatherTool(unittest.TestCase):
    """Test the WeatherTool's ability to return a mock weather report for a given location."""

    def setUp(self):
        """Set up the mock weather service before each test."""
        self.mock_weather_service = Mock(spec=protocols.WeatherServiceProtocol)

        self.tool = weather.WeatherTool(
            weather_service=self.mock_weather_service,
            location_service=Mock(spec=protocols.LocationServiceProtocol),
        )

    def _mock_current_weather_service_response(
        self, units: protocols.WeatherUnits
    ) -> dict:
        """Helper method to set up the mock weather service response based on units.

        Args:
            units (protocols.WeatherUnits): The unit system to use for the weather information.
        Returns:
            dict: A mock weather information dictionary corresponding to the specified units.
        """
        if units == protocols.WeatherUnits.METRIC:
            return {
                "temperature": "20°C",
                "feels_like": "18°C",
                "condition": "cloudy",
                "wind_speed": "5 m/s",
                "humidity": "70%",
            }
        elif units == protocols.WeatherUnits.IMPERIAL:
            return {
                "temperature": "77°F",
                "feels_like": "79°F",
                "condition": "sunny",
                "wind_speed": "10 mph",
                "humidity": "60%",
            }
        else:
            return {
                "temperature": "293 K",
                "feels_like": "291 K",
                "condition": "clear",
                "wind_speed": "3 m/s",
                "humidity": "50%",
            }

    def _mock_future_weather_service_response(
        self, units: protocols.WeatherUnits, forecast_type: str
    ) -> dict:
        """Helper method to set up the mock future weather service response based on units and forecast type.

        Args:
            units (protocols.WeatherUnits): The unit system to use for the weather information.
            forecast_type (str): The type of forecast ('daily' or 'hourly').
        Returns:
            dict: A mock future weather information dictionary corresponding to the specified units and forecast type.
        """
        if units == protocols.WeatherUnits.METRIC:
            if forecast_type == "daily":
                return {
                    "forecast": {
                        "Day": {"High": "25°C", "Low": "15°C", "Condition": "sunny"}
                    }
                }
            elif forecast_type == "hourly":
                return {
                    "forecast": {"Hour": {"Temperature": "14°C", "Condition": "cloudy"}}
                }
        elif units == protocols.WeatherUnits.IMPERIAL:
            if forecast_type == "daily":
                return {
                    "forecast": {
                        "Day": {"High": "68°F", "Low": "54°F", "Condition": "sunny"}
                    }
                }
            elif forecast_type == "hourly":
                return {
                    "forecast": {"Hour": {"Temperature": "60°F", "Condition": "sunny"}}
                }
        else:
            if forecast_type == "daily":
                return {
                    "forecast": {
                        "Day": {"High": "293 K", "Low": "285 K", "Condition": "clear"}
                    }
                }
            elif forecast_type == "hourly":
                return {
                    "forecast": {"Hour": {"Temperature": "288 K", "Condition": "clear"}}
                }
        return {"forecast": "No forecast available"}

    def test_execute_returns_weather_information(self):
        """Verify that execute() returns a dictionary containing weather information."""
        # ARRANGE
        weather_units = protocols.WeatherUnits
        test_cases = [
            {
                "location": "New York,US",
                "units": weather_units.IMPERIAL,
                "expected_result": {
                    "location": "New York,US",
                    "weather": self._mock_current_weather_service_response(
                        weather_units.IMPERIAL
                    ),
                },
            },
            {
                "location": "London,GB",
                "units": weather_units.METRIC,
                "expected_result": {
                    "location": "London,GB",
                    "weather": self._mock_current_weather_service_response(
                        weather_units.METRIC
                    ),
                },
            },
            {
                "location": "Tokyo",
                "units": weather_units.STANDARD,
                "expected_result": {
                    "location": "Tokyo",
                    "weather": self._mock_current_weather_service_response(
                        weather_units.STANDARD
                    ),
                },
            },
        ]

        for case in test_cases:
            with self.subTest(
                msg=f"Testing location '{case['location']}' with units '{case['units']}'"
            ):
                # 1. Provide the mock data
                self.mock_weather_service.get_current_weather.return_value = (
                    self._mock_current_weather_service_response(case["units"])
                )

                # 2. Execute the tool with location AND units
                result = self.tool.execute(
                    location=case["location"], units=case["units"].value
                )

                # 3. Verify the result
                self.assertEqual(result, case["expected_result"])

                # 4. Verify the service was called correctly
                self.mock_weather_service.get_current_weather.assert_called_once_with(
                    case["location"], case["units"]
                )

                # 5. Reset the mock for the next iteration
                self.mock_weather_service.reset_mock()

    def test_execute_returns_future_weather(self):
        """Verify that execute() routes 'daily' and 'hourly' forecast types through get_future_weather()."""
        # ARRANGE
        weather_units = protocols.WeatherUnits
        test_cases = [
            {
                "description": "forecast_type='daily' should call get_future_weather with forecast_type='daily'.",
                "location": "London,GB",
                "units": weather_units.METRIC,
                "forecast_type": "daily",
                "service_return": self._mock_future_weather_service_response(
                    weather_units.METRIC, "daily"
                ),
                "expected_service_call": ("London,GB", weather_units.METRIC),
                "expected_service_forecast_type": "daily",
            },
            {
                "description": "forecast_type='hourly' should call get_future_weather with forecast_type='hourly'.",
                "location": "Tokyo",
                "units": weather_units.STANDARD,
                "forecast_type": "hourly",
                "service_return": self._mock_future_weather_service_response(
                    weather_units.STANDARD, "hourly"
                ),
                "expected_service_call": ("Tokyo", weather_units.STANDARD),
                "expected_service_forecast_type": "hourly",
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["description"]):
                # 0. Reset the mock at the start of each iteration
                self.mock_weather_service.reset_mock()

                # 1. Provide the mock data
                self.mock_weather_service.get_future_weather.return_value = case[
                    "service_return"
                ]

                # 2. Execute the tool
                result = self.tool.execute(
                    location=case["location"],
                    units=case["units"].value,
                    forecast_type=case["forecast_type"],
                )

                # 3. Verify the result
                self.assertEqual(
                    result,
                    {"location": case["location"], "weather": case["service_return"]},
                )

                # 4. Verify the service was called with the correct arguments
                self.mock_weather_service.get_future_weather.assert_called_once_with(
                    *case["expected_service_call"],
                    forecast_type=case["expected_service_forecast_type"],
                )

    @patch("core.tools.weather.os.getenv")
    def test_execute_falls_back_to_ip_location(self, mock_getenv):
        """Verify that execute() calls the location service when no location is provided."""
        # ARRANGE: Ensure no environment variable is set
        mock_getenv.return_value = None

        # Mock the location service to return a valid IP lookup
        self.tool.location_service.get_location.return_value = {  # type: ignore
            "country": "GB",
            "region": "London",
        }

        # Mock the weather service response
        self.mock_weather_service.get_current_weather.return_value = {
            "condition": "sunny"
        }

        # ACT: Call execute without a location
        result = self.tool.execute(units="metric")

        # ASSERT: Verify the location service was utilized
        self.tool.location_service.get_location.assert_called_once()  # type: ignore
        self.assertEqual(result["location"], "London,GB")


if __name__ == "__main__":
    unittest.main()
