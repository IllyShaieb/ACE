"""tests.test_tools.test_entertainment_tools: This module contains tests for the entertainment tools
functionalities to ensure they work as expected."""

import unittest
from unittest import mock

import requests

from core.tools import TOOL_HANDLERS, execute_tool


@mock.patch("core.tools.entertainment.requests.get")
class TestTellJoke(unittest.TestCase):
    """Ensure the TELL_JOKE tool is registered and functions correctly."""

    def test_tell_joke_registration(self, mock_get):
        """Test that the TELL_JOKE tool is registered correctly."""

        # ARRANGE
        tool_name = "TELL_JOKE"
        expected_description = "Tells a random joke to entertain the user."

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

    def test_tell_joke_execution_success(self, mock_get):
        """Test that the TELL_JOKE tool executes correctly on successful API response."""

        # ARRANGE
        tool_name = "TELL_JOKE"
        mock_response = mock.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "setup": "Why did the scarecrow win an award?",
            "punchline": "Because he was outstanding in his field!",
        }
        mock_get.return_value = mock_response

        expected_output = (
            "Why did the scarecrow win an award?—"
            "Because he was outstanding in his field!"
        )

        # ACT
        result = execute_tool(name=tool_name, registry=TOOL_HANDLERS)

        # ASSERT
        self.assertEqual(
            result,
            expected_output,
            f"The output of the tool '{tool_name}' should be the expected joke.",
        )

    def test_tell_joke_execution_failure(self, mock_get):
        """Test that the TELL_JOKE tool handles API failure gracefully."""

        # ARRANGE
        tool_name = "TELL_JOKE"

        test_cases = [
            (
                requests.RequestException("API failure"),
                "Sorry, I couldn't fetch a joke at this time: RequestException - API failure.",
                "Errors from the API request should be handled gracefully.",
            ),
            (
                KeyError(),
                "Sorry, I couldn't understand the joke data received.",
                "Malformed JSON responses should be handled gracefully.",
            ),
        ]

        for exception, expected_output, message in test_cases:
            mock_get.side_effect = exception

            # ACT
            result = execute_tool(name=tool_name, registry=TOOL_HANDLERS)

            # ASSERT
            self.assertEqual(result, expected_output, message)


class TestFlipCoin(unittest.TestCase):
    """Ensure the FLIP_COIN tool is registered and functions correctly."""

    def test_flip_coin_registration(self):
        """Test that the FLIP_COIN tool is registered correctly."""

        # ARRANGE
        tool_name = "FLIP_COIN"
        expected_description = "Simulates a coin flip and returns the result."

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

    @mock.patch("core.tools.entertainment.random.choice")
    def test_flip_coin_execution(self, mock_choice):
        """Test that the FLIP_COIN tool executes correctly."""

        # ARRANGE
        tool_name = "FLIP_COIN"

        test_cases = [
            ("Heads", "The coin flip should return 'Heads'."),
            ("Tails", "The coin flip should return 'Tails'."),
        ]

        for mock_return, message in test_cases:
            mock_choice.return_value = mock_return

            # ACT
            result = execute_tool(name=tool_name, registry=TOOL_HANDLERS)

            # ASSERT
            self.assertEqual(result, mock_return, message)


class TestRollDice(unittest.TestCase):
    """Ensure the ROLL_DICE tool is registered and functions correctly."""

    def test_roll_dice_registration(self):
        """Test that the ROLL_DICE tool is registered correctly."""

        # ARRANGE
        tool_name = "ROLL_DICE"
        expected_description = (
            "Simulates rolling one or more dice and returns the results."
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

    @mock.patch("core.tools.entertainment.random.randint")
    def test_roll_dice_execution(self, mock_randint):
        """Test that the ROLL_DICE tool can take multiple dice sides and returns correct results."""

        # ARRANGE
        tool_name = "ROLL_DICE"

        # Check various sides
        # The result should be a string containing
        # - The dice sides rolled
        # - The individual roll results
        # - The total of the rolls
        test_cases = [
            # Single roll
            (
                [6],
                [4],
                "You rolled a 6-sided die and got: 4. Total: 4",
                "Single die roll should return correct result.",
            ),
            # Multiple rolls with same sides
            (
                [6, 6, 6],
                [2, 5, 3],
                "You rolled 3 6-sided dice and got: 2, 5, 3. Total: 10",
                "Multiple dice of same sides should return correct results.",
            ),
            # Multiple rolls with different sides
            (
                [4, 8, 10],
                [3, 7, 1],
                "You rolled the following dice: 4-sided, 8-sided, 10-sided and got: 3, 7, 1. Total: 11",
                "Multiple dice of different sides should return correct results.",
            ),
        ]

        for sides, mock_rolls, expected_output, message in test_cases:
            mock_randint.side_effect = mock_rolls

            # ACT
            result = execute_tool(name=tool_name, registry=TOOL_HANDLERS, sides=sides)

            # ASSERT
            self.assertEqual(result, expected_output, message)
