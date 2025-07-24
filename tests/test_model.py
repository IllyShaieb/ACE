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

    def test_identity_query(self):
        """Test that the model returns its identity when asked."""
        test_cases = [
            "What is your name?",
            "Who are you?",
            "What is your name",
            "Who are you",
            "Your name?",
            "What's your name?",
            "YOUR NAME PLEASE",
        ]

        # Create subTests
        for user_input in test_cases:
            with self.subTest(f"Checking '{user_input}'"):
                response = self.ace_model(user_input)
                self.assertEqual(response, "I am ACE, your personal assistant.")

    def test_creator_query(self):
        """Test that the model returns its creator's name when asked."""
        test_cases = [
            "Who created you?",
            "Who made you?",
            "Who is your creator?",
            "Who is your developer?",
        ]

        # Create subTests
        for user_input in test_cases:
            with self.subTest(f"Checking '{user_input}'"):
                response = self.ace_model(user_input)
                self.assertEqual(response, "I was created by Illy Shaieb.")


if __name__ == "__main__":
    unittest.main()
