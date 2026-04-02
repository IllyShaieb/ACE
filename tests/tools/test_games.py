"""tests.tools.test_games: Ensure that the game-related tools function correctly and return expected results."""

import unittest
from unittest.mock import patch

from core.tools import games


class TestCoinFlipTool(unittest.TestCase):
    """Test the CoinFlipTool's ability to simulate a coin flip and return a valid result."""

    def setUp(self):
        """Set up common test components."""
        self.tool = games.CoinFlipTool()

    @patch("core.tools.games.random.choice")
    def test_execute_default_single_flip(self, mock_choice):
        """Verify that execute() flips once by default."""
        # ARRANGE: Mock random.choice to return 'Heads'
        mock_choice.return_value = "Heads"

        # ACT: Execute the tool without specifying times
        result = self.tool.execute()

        # ASSERT: Verify that the result is a list with one flip result
        self.assertEqual(result, ["Heads"])

    @patch("core.tools.games.random.choice")
    def test_execute_multiple_flips_with_side_effect(self, mock_choice):
        """Verify that execute() handles multiple flips correctly."""
        # ARRANGE: Mock random.choice to return 'Heads' and 'Tails' in sequence
        mock_choice.side_effect = ["Heads", "Tails", "Heads"]

        # ACT: Execute the tool with times=3
        result = self.tool.execute(times=3)

        # ASSERT: Verify that the result is a list with the three flip results
        self.assertEqual(result, ["Heads", "Tails", "Heads"])

    @patch("core.tools.games.random.choice")
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
        self.tool = games.RollDiceTool()

    @patch("core.tools.games.random.randint")
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


if __name__ == "__main__":
    unittest.main()
