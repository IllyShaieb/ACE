"""tests.adapters.test_io: Ensures that the IO adapters in the ACE application are functioning correctly
and handling input/output as expected.
"""

import unittest
from unittest.mock import MagicMock, patch

from core import adapters
from core.views.protocols import Sender


class TestBuiltinIOAdapter(unittest.TestCase):
    """Test the BuiltinIOAdapter's ability to get input and display output using
    Python's built-in functions."""

    def setUp(self) -> None:
        """Set up common test components."""
        self.adapter = adapters.BuiltinIOAdapter()

    @patch("builtins.input", return_value="test input")
    def test_get_input(self, mock_input):
        """Test that the get_input method calls the built-in input function with the
        correct prompt."""
        # ACT: Call the get_input method of the adapter
        result = self.adapter.get_input("Enter something: ")

        # ASSERT: Verify that the input function was called with the correct prompt and
        # returned the expected value
        mock_input.assert_called_once_with("Enter something: ")
        self.assertEqual(result, "test input")

    @patch("builtins.print")
    def test_display_output(self, mock_print):
        """Test that the display_output method calls the built-in print function with
        the correct message."""
        # ACT: Call the display_output method of the adapter
        self.adapter.display_output("Hello, World!")

        # ASSERT: Verify that the print function was called with the correct message
        mock_print.assert_called_once_with("Hello, World!")

    @patch("builtins.print")
    def test_display_output_with_sender_info(self, mock_print):
        """Test that display_output prints the bare message for INFO sender."""
        self.adapter.display_output("System ready", sender=Sender.INFO)
        mock_print.assert_any_call("System ready")

    @patch("builtins.print")
    def test_display_output_with_sender_prefixes_label(self, mock_print):
        """Test that display_output prefixes non-INFO senders with their value."""
        self.adapter.display_output("Hello!", sender=Sender.ACE)
        mock_print.assert_any_call("ACE: Hello!")


class TestRichIOAdapter(unittest.TestCase):
    """Test RichIOAdapter session-selection behavior."""

    def setUp(self) -> None:
        self.adapter = adapters.RichIOAdapter()
        self.adapter.console = MagicMock()

    def test_get_session_choice_returns_none_for_new_conversation(self):
        """Selecting 0 should start a new conversation."""
        sessions = [
            {
                "session_id": "session-1",
                "title": "Existing Session",
                "updated_at": "2026-03-12 12:00:00",
            }
        ]
        self.adapter.console.input.return_value = "0"

        result = self.adapter.get_session_choice(sessions)

        self.assertIsNone(result)

    def test_get_session_choice_retries_after_invalid_selection(self):
        """Invalid selections should print an error and reprompt until valid."""
        sessions = [
            {
                "session_id": "session-1",
                "title": "Existing Session",
                "updated_at": "2026-03-12 12:00:00",
            }
        ]
        self.adapter.console.input.side_effect = ["99", "1"]

        result = self.adapter.get_session_choice(sessions)

        self.assertEqual(result, "session-1")
        self.assertEqual(self.adapter.console.input.call_count, 2)
        self.adapter.console.print.assert_any_call(
            "[red]Invalid selection. Please try again.[/red]"
        )


if __name__ == "__main__":
    unittest.main()
