"""tests.test_tools.test_web_tools: This module contains tests for the web tools
functionalities to ensure they work as expected."""

import unittest
from unittest import mock

import requests

from core.tools import TOOL_HANDLERS, execute_tool


@mock.patch("core.tools.web_tools.requests.get")
class TestGetWeather(unittest.TestCase):
    """Ensure the GET_WEATHER tool is registered and functions correctly."""

    def test_get_weather_registration(self, mock_get):
        """Test that the GET_WEATHER tool is registered correctly."""

        # ARRANGE
        tool_name = "GET_WEATHER"
        expected_description = (
            "Fetches and returns the current weather for a specified location."
        )

        # ACT
        tool_handler = TOOL_HANDLERS.get(tool_name)

        # ASSERT
        self.assertIsNotNone(
            tool_handler,
            f"The tool '{tool_name}' should be registered in TOOL_HANDLERS.",
        )

        if tool_handler:
            self.assertEqual(
                tool_handler.description,
                expected_description,
                f"The description of the tool '{tool_name}' should be '{expected_description}'.",
            )

    def test_get_weather_no_location(self, mock_get):
        """Test the GET_WEATHER tool with no location provided."""

        # ARRANGE
        tool_name = "GET_WEATHER"
        input_location = ""
        expected_response = "What location would you like to know the weather for?"

        # ACT
        response = execute_tool(
            tool_name, registry=TOOL_HANDLERS, location=input_location
        )

        # ASSERT
        self.assertEqual(
            response,
            expected_response,
            "The GET_WEATHER tool should prompt for a location when none is provided.",
        )

    def test_get_weather_missing_api_key(self, mock_get):
        """Test the GET_WEATHER tool when the WEATHER_API_KEY is missing."""

        # ARRANGE
        tool_name = "GET_WEATHER"
        input_location = "New York"
        expected_response = "Apologies, it appears the WEATHER_API_KEY is not set."

        # ACT
        with mock.patch.dict("os.environ", {"WEATHER_API_KEY": ""}):
            response = execute_tool(
                tool_name, registry=TOOL_HANDLERS, location=input_location
            )

        # ASSERT
        self.assertEqual(
            response,
            expected_response,
            "The GET_WEATHER tool should notify about missing API key.",
        )

    def test_get_weather_successful(self, mock_get):
        """Test the GET_WEATHER tool with a successful API response."""

        # ARRANGE
        tool_name = "GET_WEATHER"
        input_location = "London"
        mock_get.return_value.json.return_value = {
            "location": {
                "name": "London",
                "region": "City of London, Greater London",
                "country": "United Kingdom",
                "lat": 51.5171,
                "lon": -0.1062,
                "tz_id": "Europe/London",
                "localtime_epoch": 1760610582,
                "localtime": "2025-10-16 11:29",
            },
            "current": {
                "last_updated_epoch": 1760609700,
                "last_updated": "2025-10-16 11:15",
                "temp_c": 13.2,
                "temp_f": 55.8,
                "is_day": 1,
                "condition": {
                    "text": "Partly cloudy",
                    "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png",
                    "code": 1003,
                },
                "wind_mph": 6.5,
                "wind_kph": 10.4,
                "wind_degree": 60,
                "wind_dir": "ENE",
                "pressure_mb": 1028.0,
                "pressure_in": 30.36,
                "precip_mm": 0.0,
                "precip_in": 0.0,
                "humidity": 82,
                "cloud": 50,
                "feelslike_c": 12.4,
                "feelslike_f": 54.3,
                "windchill_c": 15.8,
                "windchill_f": 60.4,
                "heatindex_c": 15.8,
                "heatindex_f": 60.4,
                "dewpoint_c": 5.9,
                "dewpoint_f": 42.6,
                "vis_km": 10.0,
                "vis_miles": 6.0,
                "uv": 1.0,
                "gust_mph": 8.0,
                "gust_kph": 12.9,
            },
        }

        # ACT
        with mock.patch.dict("os.environ", {"WEATHER_API_KEY": "dummy_key"}):
            response = execute_tool(
                tool_name, registry=TOOL_HANDLERS, location=input_location
            )

        # ASSERT

        # The response should contain key weather details
        key_details = [
            ("London", "location name"),
            ("City of London, Greater London", "region"),
            ("United Kingdom", "country"),
            ("13.2°C", "temperature"),
            ("Partly cloudy", "condition"),
            ("10.4 kph", "wind speed"),
            ("82%", "humidity"),
            ("12.4°C", "feels like temperature"),
        ]

        for detail, description in key_details:
            self.assertIn(
                detail,
                response,
                f"The GET_WEATHER tool response should include the {description}: {detail}.",
            )

    def test_get_weather_api_error(self, mock_get):
        """Test the GET_WEATHER tool when the API request fails."""

        # ARRANGE
        tool_name = "GET_WEATHER"
        input_location = "InvalidLocation"
        mock_get.side_effect = requests.RequestException("API request failed")

        expected_response = "An error occurred while fetching the weather data: RequestException - API request failed"

        # ACT
        with mock.patch.dict("os.environ", {"WEATHER_API_KEY": "dummy_key"}):
            response = execute_tool(
                tool_name, registry=TOOL_HANDLERS, location=input_location
            )

        # ASSERT
        self.assertEqual(
            response,
            expected_response,
            "The GET_WEATHER tool should handle API request exceptions gracefully.",
        )

    def test_get_weather_invalid_response(self, mock_get):
        """Test the GET_WEATHER tool with an invalid API response structure."""

        # ARRANGE
        tool_name = "GET_WEATHER"
        input_location = "Nowhere"
        mock_get.return_value.json.return_value = {
            "invalid": "data"
        }  # Missing expected keys

        expected_response = "Received unexpected data format from the weather service: KeyError - 'location'"

        # ACT
        with mock.patch.dict("os.environ", {"WEATHER_API_KEY": "dummy_key"}):
            response = execute_tool(
                tool_name, registry=TOOL_HANDLERS, location=input_location
            )

        # ASSERT
        self.assertEqual(
            response,
            expected_response,
            "The GET_WEATHER tool should handle invalid API responses gracefully.",
        )


class TestWebSearch(unittest.TestCase):
    """Ensure the WEB_SEARCH tool is registered and functions correctly."""

    def test_web_search_registration(self):
        """Test that the WEB_SEARCH tool is registered correctly."""

        # ARRANGE
        tool_name = "WEB_SEARCH"
        expected_description = "Performs a web search and returns a summary of results."

        # ACT
        tool_handler = TOOL_HANDLERS.get(tool_name)

        # ASSERT
        self.assertIsNotNone(
            tool_handler,
            f"The tool '{tool_name}' should be registered in TOOL_HANDLERS.",
        )

        if tool_handler:
            self.assertEqual(
                tool_handler.description,
                expected_description,
                f"The description of the tool '{tool_name}' should be '{expected_description}'.",
            )

    def test_web_search_no_query(self):
        """Test the WEB_SEARCH tool with no query provided."""

        # ARRANGE
        tool_name = "WEB_SEARCH"
        input_query = ""
        expected_response = "What would you like to search for?"

        # ACT
        response = execute_tool(tool_name, registry=TOOL_HANDLERS, query=input_query)

        # ASSERT
        self.assertEqual(
            response,
            expected_response,
            "The WEB_SEARCH tool should prompt for a query when none is provided.",
        )

    @mock.patch(
        "core.tools.web_tools.scrape_and_summarise", return_value="Sample summary."
    )
    def test_web_search_with_query(self, mock_scrape_and_summarise):
        """Test the WEB_SEARCH tool with a valid query."""

        # ARRANGE
        tool_name = "WEB_SEARCH"
        input_query = "Python programming"
        expected_response_start = '# Search Results for: "Python programming"'

        expected_headings = [
            "## Text Results",
            "## News Results",
        ]

        # ACT
        response = execute_tool(tool_name, registry=TOOL_HANDLERS, query=input_query)

        # ASSERT
        self.assertTrue(
            response.startswith(expected_response_start),
            "The WEB_SEARCH tool should return a summary starting with the expected header.",
        )
        for heading in expected_headings:
            self.assertIn(
                heading,
                response,
                f"The WEB_SEARCH tool response should include the heading: {heading}.",
            )


if __name__ == "__main__":
    unittest.main()
