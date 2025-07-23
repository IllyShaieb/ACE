"""test_model.py: Unit tests for the model class."""

import unittest
from core.model import ACEModel


class TestACEModel(unittest.TestCase):
    """Test cases for the ACEModel class."""

    def setUp(self):
        self.ace_model = ACEModel()

    def test_unrecognised_query(self):
        """Test that the model returns the default response in response to an unknown query."""
        test_cases = [
            ("", "Check for empty input"),
            (" ", "Check for whitespace input"),
            ("random gibberish", "Check for random input"),
        ]

        # Create subTests
        for user_input, scenario_desc in test_cases:
            with self.subTest(scenario_desc):
                response = self.ace_model(user_input)
                self.assertEqual(response, "Sorry, I don't understand.")


if __name__ == "__main__":
    unittest.main()
