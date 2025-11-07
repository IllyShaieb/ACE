"""test_actions.py: Contains tests for the actions in the ACE program.

Ensures that the action can return the expected results for various inputs.
"""

import unittest
from unittest import mock

import requests

from core import actions


class TestActionHandling(unittest.TestCase):
    """Tests for the core action handling mechanism."""

    def test_action_handler_registration(self):
        """Ensure action handlers can be registered and executed."""

        @actions.register_handler("TEST_ACTION")
        def test_action():
            return "Test Passed"

        self.assertIn("TEST_ACTION", actions.ACTION_HANDLERS)

        handler_info = actions.ACTION_HANDLERS["TEST_ACTION"]
        self.assertEqual(
            handler_info.handler,
            test_action,
            "Handler function should be in ACTION_HANDLERS",
        )
        self.assertFalse(
            handler_info.requires_user_input,
            "requires_user_input should be False by default",
        )
        self.assertEqual(
            handler_info.handler(),
            "Test Passed",
            "Handler function should return expected result",
        )

    def test_action_handler_registration_with_input(self):
        """Ensure action handlers can be registered with requires_user_input=True."""

        @actions.register_handler("TEST_ACTION_INPUT", requires_user_input=True)
        def test_action_input(user_input: str) -> str:
            return f"Input Received: {user_input}"

        self.assertIn("TEST_ACTION_INPUT", actions.ACTION_HANDLERS)

        handler_info = actions.ACTION_HANDLERS["TEST_ACTION_INPUT"]
        self.assertEqual(
            handler_info.handler,
            test_action_input,
            "Handler function should be in ACTION_HANDLERS",
        )
        self.assertTrue(
            handler_info.requires_user_input,
            "requires_user_input should be True",
        )
        self.assertEqual(
            handler_info.handler("Sample Input"),
            "Input Received: Sample Input",
            "Handler function should return expected result with input",
        )

    def test_register_duplicate_handlers(self):
        """Ensure registering a duplicate handler warns and overwrites."""

        # Register the first handler
        @actions.register_handler("DUPLICATE_ACTION")
        def first_handler():
            return "First Handler"

        # Check that a warning is issued when overwriting the handler
        with self.assertWarns(Warning):

            @actions.register_handler("DUPLICATE_ACTION")
            def second_handler():
                return "Second Handler"

        handler_info = actions.ACTION_HANDLERS["DUPLICATE_ACTION"]
        self.assertEqual(
            handler_info.handler,
            second_handler,
            "The second handler should overwrite the first one",
        )
        self.assertEqual(
            handler_info.handler(),
            "Second Handler",
            "Handler function should return result from the second handler",
        )

    def test_execute_action_known(self):
        """Ensure known actions return the expected results."""
        self.assertIn("ACE", actions.execute_action("IDENTIFY_SELF"))

    def test_execute_action_unknown(self):
        """Ensure unknown actions return the unknown action message."""
        self.assertEqual(
            actions.execute_action("DO_NOTHING"), actions.UNKNOWN_ACTION_MESSAGE
        )


class TestIdentifySelfAction(unittest.TestCase):
    """Tests for the Identify Self action."""

    def test_handle_identify(self):
        """Ensure the identify self action returns the correct identifier."""
        self.assertIn("ACE", actions.execute_action("IDENTIFY_SELF"))


class TestSelfCreatorAction(unittest.TestCase):
    """Tests for the Self Creator action."""

    def test_handle_self_creator(self):
        """Ensure the creator action returns the correct creator name."""
        self.assertIn("Illy Shaieb", actions.execute_action("SELF_CREATOR"))


class TestGetTimeAction(unittest.TestCase):
    """Tests for the Get Time action."""

    def test_handle_get_time(self):
        """Ensure the get_time action returns the current time."""
        self.assertIn("The current time is", actions.execute_action("GET_TIME"))


class TestGetDateAction(unittest.TestCase):
    """Tests for the Get Date action."""

    def test_handle_get_date(self):
        """Ensure the get_date action returns today's date."""
        self.assertIn("Today's date is", actions.execute_action("GET_DATE"))


class TestHelpAction(unittest.TestCase):
    """Tests for the Help action."""

    def test_handle_help(self):
        """Ensure the help action returns a list of available actions."""
        self.assertIn("assist", actions.execute_action("HELP"))


class TestFlipCoinAction(unittest.TestCase):
    """Tests for the Flip Coin action."""

    def test_handle_flip_coin(self):
        """Ensure the flip_coin action returns either 'Heads' or 'Tails'."""
        self.assertIn(actions.execute_action("FLIP_COIN"), ["Heads", "Tails"])


class TestRollDiceAction(unittest.TestCase):
    """Tests for the Roll Dice action."""

    def test_handle_roll_dice(self):
        """Ensure the roll_dice action correctly returns a single die roll result."""
        # FIX: The 'sides' argument is required.
        result = actions.execute_action("ROLL_DICE", sides=[6])
        self.assertIsInstance(result, str)

        # Result should be like "You rolled a {sides}-sided die and got: {result}. Total: {total}"
        self.assertIn("You rolled a", result)
        self.assertIn("6-sided", result)

        # FIX: Parse the result correctly
        dice_roll = int(result.split("got: ")[1].split(".")[0])
        self.assertIn(dice_roll, range(1, 7), "Dice roll should be between 1 and 6")

    def test_handle_roll_dice_custom_sides(self):
        """Ensure the roll_dice action correctly handles custom sides."""
        result = actions.execute_action("ROLL_DICE", sides=[20])
        self.assertIsInstance(result, str)

        self.assertIn("You rolled a", result)
        self.assertIn("20-sided", result)

        # FIX: Parse the result correctly
        dice_roll = int(result.split("got: ")[1].split(".")[0])
        self.assertIn(dice_roll, range(1, 21), "Dice roll should be between 1 and 20")

    def test_handle_multiple_dice(self):
        """Ensure the roll_dice action can handle multiple dice rolls."""
        test_cases = [
            {
                "sides": [6, 6],
                "expected_range": (2, 12),
                "expected_str": "You rolled 2 6-sided dice",
            },
            {
                "sides": [6, 20],
                "expected_range": (2, 26),
                "expected_str": "You rolled 6-sided, 20-sided dice",
            },
            {
                "sides": [4, 8, 12],
                "expected_range": (3, 24),
                "expected_str": "You rolled 4-sided, 8-sided, 12-sided dice",
            },
        ]
        for case in test_cases:
            with self.subTest(sides=case["sides"]):
                sides_list = case["sides"]
                expected_min, expected_max = case["expected_range"]

                result = actions.execute_action("ROLL_DICE", sides=sides_list)
                self.assertIsInstance(result, str)

                # FIX: Check for the new response format
                self.assertIn(case["expected_str"], result)
                self.assertIn("Total: ", result)

                # Extract the total from the result string
                total_str = result.split("Total: ")[1]
                total = int(total_str)
                self.assertIn(
                    total,
                    range(expected_min, expected_max + 1),
                    "Total should be within the expected range",
                )

    def test_handle_roll_dice_no_sides(self):
        """Ensure the roll_dice action handles no sides provided."""
        result = actions.execute_action("ROLL_DICE", sides=[])
        self.assertIsInstance(result, str)

        # Should default to rolling a single 6-sided die
        self.assertIn("You rolled a 6-sided die", result)


class TestGetWeatherAction(unittest.TestCase):
    """Tests for the Get Weather action."""

    @mock.patch("core.actions.requests.get")
    def test_handle_get_weather(self, mock_get):
        """Ensure the get_weather action returns the current weather information."""
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
        result = actions.execute_action("GET_WEATHER", location="London")

        # Check the result contains expected weather information
        # Note: just checking for key substrings to avoid brittleness
        self.assertIn("London", result, "Result should mention London")
        self.assertIn(
            "partly cloudy",
            result.lower(),
            "Result should mention the weather condition",
        )
        self.assertIn("13.2°C", result, "Result should mention the current temperature")
        self.assertIn(
            "12.4°C", result, "Result should mention the feels like temperature"
        )

    @mock.patch("core.actions.requests.get")
    def test_handle_get_weather_handle_http_error(self, mock_get):
        """Ensure the get_weather action handles HTTP errors gracefully."""
        mock_get.side_effect = requests.exceptions.RequestException(
            "Testing HTTP Error"
        )
        result = actions.execute_action("GET_WEATHER", location="London")
        self.assertIn("Testing HTTP Error", result)

    @mock.patch("core.actions.requests.get")
    def test_handle_get_weather_handle_unexpected_json(self, mock_get):
        """Ensure the get_weather action handles unexpected JSON structure gracefully."""
        mock_get.return_value.json.return_value = {"unexpected_key": "unexpected_value"}
        result = actions.execute_action("GET_WEATHER", location="London")
        self.assertIn(
            "Received unexpected data format from the weather service", result
        )

    @mock.patch("core.actions.requests.get")
    def test_handle_get_weather_handle_general_exception(self, mock_get):
        """Ensure the get_weather action handles general exceptions gracefully."""
        mock_get.side_effect = Exception("General Exception for Testing")
        result = actions.execute_action("GET_WEATHER", location="London")
        self.assertIn("An unknown issue occurred during the weather retrieval", result)

    @mock.patch("core.actions.requests.get")
    def test_handle_get_weather_missing_location(self, mock_get):
        """Ensure the get_weather action handles missing location in query."""
        result = actions.execute_action("GET_WEATHER", location=None)
        self.assertIn("What location would you like to know the weather for?", result)

    @mock.patch("core.actions.os.getenv")
    def test_handle_get_weather_missing_api_key(self, mock_getenv):
        """Ensure the get_weather action handles missing API key."""
        mock_getenv.return_value = None
        result = actions.execute_action("GET_WEATHER", location="London")
        self.assertIn("Apologies, it appears the WEATHER_API_KEY is not set.", result)


if __name__ == "__main__":
    unittest.main()
