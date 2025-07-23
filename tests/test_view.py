"""test_view.py: Unit tests for the view module."""

import unittest
from unittest.mock import patch
import io


from core.view import IACEView, ConsoleView


class TestConsoleView(unittest.TestCase):
    """Test cases for the ConsoleView class."""

    def setUp(self):
        """Set up for test methods.

        This method is called before each test function is executed.
        It initialises a fresh ConsoleView instance for each test.
        """
        self.console_view = ConsoleView()

    def test_console_view_implements_iaceview(self):
        """Test that ConsoleView correctly implements the IACEView Protocol."""
        # This uses the @runtime_checkable decorator on IACEView
        self.assertTrue(isinstance(self.console_view, IACEView))

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_display_message(self, mock_stdout):
        """Test that display_message prints the correct format to stdout."""
        # First message
        sender1 = "ACE"
        message1 = "Hello, how can I help?"
        self.console_view.display_message(sender1, message1)
        self.assertEqual(mock_stdout.getvalue(), f"{sender1}: {message1}\n")

        # Second message - output should be cumulative
        sender2 = "YOU"
        message2 = "I need assistance."
        self.console_view.display_message(sender2, message2)
        # The expected output should be the first message + the second message
        expected_cumulative_output = f"{sender1}: {message1}\n{sender2}: {message2}\n"
        self.assertEqual(mock_stdout.getvalue(), expected_cumulative_output)

    @patch("builtins.input", return_value="test user input")
    def test_get_user_input(self, mock_input):
        """Test that get_user_input correctly captures and strips user input."""
        prompt = "Enter your command: "
        user_input = self.console_view.get_user_input(prompt)
        mock_input.assert_called_once_with(prompt)
        self.assertEqual(user_input, "test user input")

        # Test with leading/trailing whitespace
        mock_input.return_value = "  another input  "
        user_input = self.console_view.get_user_input("Prompt 2: ")
        self.assertEqual(user_input, "another input")

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_show_error(self, mock_stdout):
        """Test that show_error prints the correct error format to stdout."""
        error_message = "Database connection failed."
        self.console_view.show_error(error_message)
        self.assertEqual(mock_stdout.getvalue(), f"[ERROR] {error_message}\n")

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_show_info(self, mock_stdout):
        """Test that show_info prints the correct informational message to stdout."""
        info_message = "Application starting..."
        self.console_view.show_info(info_message)
        self.assertEqual(mock_stdout.getvalue(), f"[INFO] {info_message}\n")


if __name__ == "__main__":
    unittest.main()
