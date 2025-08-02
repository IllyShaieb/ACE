"""test_actions.py: Contains tests for the actions in the ACE program.

Ensures that the action can return the expected results for various inputs.
"""

import unittest
from core import actions


class TestActionHandlers(unittest.TestCase):
    """Tests to ensure action handlers return expected results."""

    def test_action_handler_registration(self):
        """Ensure action handlers can be registered and executed."""

        @actions.register_handler("TEST_ACTION")
        def test_action():
            return "Test Passed"

        self.assertIn("TEST_ACTION", actions.ACTION_HANDLERS)
        self.assertEqual(actions.ACTION_HANDLERS["TEST_ACTION"](), "Test Passed")

    def test_execute_action_known(self):
        """Ensure known actions return the expected results."""
        self.assertIn("ACE", actions.execute_action("IDENTIFY"))

    def test_execute_action_unknown(self):
        """Ensure unknown actions return the unknown action message."""
        self.assertEqual(
            actions.execute_action("DO_NOTHING"), actions.UNKNOWN_ACTION_MESSAGE
        )

    def test_handle_greet(self):
        """Ensure the greet action returns a greeting message."""
        self.assertIn("Hello", actions.handle_greet())

    def test_handle_identify(self):
        """Ensure the identify action returns the correct identifier."""
        self.assertIn("ACE", actions.handle_identify())

    def test_handle_creator(self):
        """Ensure the creator action returns the correct creator name."""
        self.assertIn("Illy Shaieb", actions.handle_creator())

    def test_handle_get_time(self):
        """Ensure the get_time action returns the current time."""
        result = actions.handle_get_time()
        self.assertIn("The current time is", result)

    def test_handle_get_date(self):
        """Ensure the get_date action returns today's date."""
        result = actions.handle_get_date()
        self.assertIn("Today's date is", result)

    def test_handle_help(self):
        """Ensure the help action returns a list of available actions."""
        self.assertIn("assist", actions.handle_help())

    def test_handle_flip_coin(self):
        """Ensure the flip_coin action returns either 'Heads' or 'Tails'."""
        self.assertIn(actions.handle_flip_coin(), ["Heads", "Tails"])

    def test_handle_roll_die(self):
        """Ensure the roll_die action returns a number between 1 and 6."""
        # Must be a string representation of the number
        result = actions.handle_roll_die()
        self.assertIsInstance(result, str)

        # Convert to integer and check the range
        value = int(result)
        self.assertIn(value, range(1, 7))


if __name__ == "__main__":
    unittest.main()
