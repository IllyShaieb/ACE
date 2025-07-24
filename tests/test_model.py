"""test_model.py: Unit tests for the model class."""

import unittest
from core.model import ACEModel


class TestACEModel(unittest.TestCase):
    """Test cases for the ACEModel class."""

    @classmethod
    def setUpClass(cls):
        cls.ace_model = ACEModel()

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

    def test_greeting_query(self):
        """Test that the model returns a specific response when greeted."""
        test_cases = ["Hello", "Hi there", "Greetings", "Hey!", "Good Morning"]

        # Create subTests
        for user_input in test_cases:
            with self.subTest(f"Checking '{user_input}'"):
                response = self.ace_model(user_input)
                self.assertEqual(response, "Hello! How can I assist you today?")


if __name__ == "__main__":
    unittest.main()
