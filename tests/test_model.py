"""test_model.py: Unit tests for the model class."""

import unittest
from core.model import ACEModel


class TestACEModel(unittest.TestCase):
    """Test cases for the ACEModel class."""

    @classmethod
    def setUpClass(cls):
        cls.ace_model = ACEModel()

    def test_unrecognised_query(self):
        """Test that the model returns an empty list for an unknown query."""
        test_cases = [
            ("", "Check for empty input"),
            (" ", "Check for whitespace input"),
            ("random gibberish", "Check for random input"),
        ]

        # Create subTests
        for user_input, scenario_desc in test_cases:
            with self.subTest(scenario_desc):
                response = self.ace_model(user_input)
                self.assertEqual(response, [])

    def test_single_intent_queries(self):
        """Test that the model correctly identifies single, distinct intents."""
        test_cases = {
            "GREET": ["Hello", "Hi there", "Hey!"],
            "IDENTIFY": ["What is your name?", "Who are you?"],
            "CREATOR": ["Who created you?", "Who made you?"],
            "HELP": ["Can you help me?", "I need assistance"],
            "JOKE": ["Tell me a joke", "Make me laugh"],
            "GET_TIME": ["What time is it?", "Tell me the time"],
            "GET_DATE": ["What is the date today?", "Tell me today's date"],
            "FLIP_COIN": ["Flip a coin", "Toss a coin"],
            "ROLL_DIE": ["Roll a die", "Roll a dice"],
        }

        for expected_action, queries in test_cases.items():
            for query in queries:
                with self.subTest(f"Query: '{query}' -> Action: '{expected_action}'"):
                    actions = self.ace_model(query)
                    self.assertEqual(actions, [expected_action])

    def test_multi_intent_prioritisation(self):
        """
        Test that the model returns only the action with the highest priority
        when multiple intents of different priorities are present.
        """
        user_input = "Hello, who are you?"

        # 'IDENTIFY' (priority 2) should be chosen over 'GREET' (priority 1)
        expected_actions = ["IDENTIFY"]

        actions = self.ace_model(user_input)

        self.assertEqual(actions, expected_actions)

    def test_multi_intent_same_priority(self):
        """
        Test that the model returns all actions when multiple intents
        of the same highest priority are present.
        """
        user_input = "What's your name and who created you?"

        # Both IDENTIFY and CREATOR have priority 2
        expected_actions = ["IDENTIFY", "CREATOR"]

        actions = self.ace_model(user_input)

        # Use assertCountEqual because the order of actions is not guaranteed
        self.assertCountEqual(actions, expected_actions)

    def test_low_priority_intent_only(self):
        """
        Test that a low-priority intent is returned correctly when it's the
        only one present.
        """
        user_input = "good morning"
        expected_actions = ["GREET"]  # GREET has the lowest priority

        actions = self.ace_model(user_input)

        self.assertEqual(actions, expected_actions)


if __name__ == "__main__":
    unittest.main()
