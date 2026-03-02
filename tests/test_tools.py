"""test_tools.py: Ensure that the tools are correctly implemented and can be called as expected."""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from core import protocols, tools


class TestClockTool(unittest.TestCase):
    """Test the ClockTool's ability to execute and return the current date and time."""

    def setUp(self):
        """Set up common test components."""
        self.tool = tools.ClockTool()

    def test_execute_returns_current_date_time(self):
        """Verify that `execute()` returns a string representing the current date and time."""
        # ARRANGE: Define a fixed datetime for testing
        fixed_datetime = datetime(2026, 1, 1, 12, 0, 0)
        with patch("core.tools.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_datetime

            # ACT: Execute the tool
            result = self.tool.execute()

            # ASSERT: Verify the result matches the expected string
            self.assertIsInstance(result, str)
            self.assertEqual(result, "2026-01-01T12:00:00")

    def test_execute_with_format_parameter(self):
        """Verify that `execute()` returns the correct format based on the 'format' parameter."""
        # ARRANGE: Define a fixed datetime for testing
        fixed_datetime = datetime(2026, 1, 1, 12, 0, 0)
        with patch("core.tools.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_datetime

            # ACT & ASSERT: Test different format options
            self.assertEqual(self.tool.execute(format="time"), "12:00:00")
            self.assertEqual(self.tool.execute(format="date"), "2026-01-01")
            self.assertEqual(self.tool.execute(format="both"), "2026-01-01T12:00:00")


class TestCharacterCounterTool(unittest.TestCase):
    """Test the CharacterCounterTool's ability to count characters in a given input string."""

    def setUp(self):
        """Set up common test components."""
        self.tool = tools.CharacterCounterTool()

    def test_execute_counts_characters(self):
        """Verify that `execute()` correctly counts the number of characters in the input string."""
        # ARRANGE: Define the input string and expected character count
        test_cases = [
            {
                "input_string": "",
                "with_spaces": True,
                "character": None,
                "expected_count": 0,
                "description": "Empty string should return 0.",
            },
            {
                "input_string": "Hello",
                "with_spaces": True,
                "character": None,
                "expected_count": 5,
                "description": "Simple word should return correct count.",
            },
            {
                "input_string": "ACE - The Artificial Consciousness Engine",
                "with_spaces": True,
                "character": None,
                "expected_count": 41,
                "description": "Longer sentence should return correct count.",
            },
            {
                "input_string": "   Leading and trailing spaces   ",
                "with_spaces": True,
                "character": None,
                "expected_count": 33,
                "description": "String with spaces should return correct count.",
            },
            {
                "input_string": "Count only letters",
                "with_spaces": False,
                "character": None,
                "expected_count": 16,
                "description": "Count characters without spaces.",
            },
            {
                "input_string": "Count only 'o' characters",
                "with_spaces": True,
                "character": "o",
                "expected_count": 3,
                "description": "Count only specific character 'o'.",
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["description"]):
                # ACT: Execute the tool with the input string
                result = self.tool.execute(
                    input_string=case["input_string"],
                    with_spaces=case["with_spaces"],
                    character=case["character"],
                )

                # ASSERT: Verify the result matches the expected character count
                self.assertIsInstance(result, int)
                self.assertEqual(result, case["expected_count"])


class TestCoinFlipTool(unittest.TestCase):
    """Test the CoinFlipTool's ability to simulate a coin flip and return a valid result."""

    def setUp(self):
        """Set up common test components."""
        self.tool = tools.CoinFlipTool()

    @patch("core.tools.random.choice")
    def test_execute_default_single_flip(self, mock_choice):
        """Verify that execute() flips once by default."""
        # ARRANGE: Mock random.choice to return 'Heads'
        mock_choice.return_value = "Heads"

        # ACT: Execute the tool without specifying times
        result = self.tool.execute()

        # ASSERT: Verify that the result is a list with one flip result
        self.assertEqual(result, ["Heads"])

    @patch("core.tools.random.choice")
    def test_execute_multiple_flips_with_side_effect(self, mock_choice):
        """Verify that execute() handles multiple flips correctly."""
        # ARRANGE: Mock random.choice to return 'Heads' and 'Tails' in sequence
        mock_choice.side_effect = ["Heads", "Tails", "Heads"]

        # ACT: Execute the tool with times=3
        result = self.tool.execute(times=3)

        # ASSERT: Verify that the result is a list with the three flip results
        self.assertEqual(result, ["Heads", "Tails", "Heads"])

    @patch("core.tools.random.choice")
    def test_execute_zero_or_negative_times(self, mock_choice):
        """Verify that invalid flip counts are handled gracefully."""
        # ARRANGE: Mock random.choice to return 'Tails'
        mock_choice.return_value = "Tails"
        test_cases = [0, -1, -10]

        for times in test_cases:
            with self.subTest(msg=f"Testing times={times}"):
                # ACT: Execute the tool with invalid times
                result = self.tool.execute(times=times)

                # ASSERT: Verify that the result defaults to an empty list
                self.assertEqual(result, [])
                mock_choice.assert_not_called()


class TestRollDiceTool(unittest.TestCase):
    """Test the RollDiceTool's ability to simulate rolling dice and return valid results."""

    def setUp(self):
        """Set up common test components."""
        self.tool = tools.RollDiceTool()

    @patch("core.tools.random.randint")
    def test_execute_returns_dice_results(self, mock_randint):
        """Verify that execute() can handle rolling dice with any specified sides and times."""
        # ARRANGE
        test_cases = [
            {
                "dice": None,
                "mock_randint_return": [4],
                "expected_result": [("1d6", [4])],
                "description": "Default to rolling one d6 when no dice specified.",
            },
            {
                "dice": ["2d6"],
                "mock_randint_return": [3, 5],
                "expected_result": [("2d6", [3, 5])],
                "description": "Rolling two d6 should return two results.",
            },
            {
                "dice": ["1d10", "3d4"],
                "mock_randint_return": [7, 2, 3, 1],
                "expected_result": [("1d10", [7]), ("3d4", [2, 3, 1])],
                "description": "Rolling multiple dice with different sides should return correct results.",
            },
            {
                "dice": ["d20"],
                "mock_randint_return": [15],
                "expected_result": [("d20", [15])],
                "description": "Rolling a d20 should return a result between 1 and 20.",
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["description"]):
                # ACT: Execute the tool with the specified dice
                mock_randint.side_effect = case["mock_randint_return"]
                result = self.tool.execute(dice=case["dice"])

                # ASSERT: Verify that the result matches the expected result
                self.assertEqual(result, case["expected_result"])


class TestWeatherTool(unittest.TestCase):
    """Test the WeatherTool's ability to return a mock weather report for a given location."""

    def setUp(self):
        """Set up common test components."""
        self.mock_service = Mock(spec=protocols.WeatherServiceProtocol)
        self.tool = tools.WeatherTool(weather_service=self.mock_service)

    def _mock_weather_service_response(self, units: protocols.WeatherUnits) -> dict:
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
                    "weather": self._mock_weather_service_response(
                        weather_units.IMPERIAL
                    ),
                },
            },
            {
                "location": "London,GB",
                "units": weather_units.METRIC,
                "expected_result": {
                    "location": "London,GB",
                    "weather": self._mock_weather_service_response(
                        weather_units.METRIC
                    ),
                },
            },
            {
                "location": "Tokyo",
                "units": weather_units.STANDARD,
                "expected_result": {
                    "location": "Tokyo",
                    "weather": self._mock_weather_service_response(
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
                self.mock_service.get_current_weather.return_value = (
                    self._mock_weather_service_response(case["units"])
                )

                # 2. Execute the tool with location AND units
                result = self.tool.execute(
                    location=case["location"], units=case["units"].value
                )

                # 3. Verify the result
                self.assertEqual(result, case["expected_result"])

                # 4. Verify the service was called correctly
                self.mock_service.get_current_weather.assert_called_once_with(
                    case["location"], case["units"]
                )

                # 5. Reset the mock for the next iteration
                self.mock_service.reset_mock()


if __name__ == "__main__":
    unittest.main()
