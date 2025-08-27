"""test_view.py: Unit tests for the view module."""

import io
import tkinter as tk
import unittest
from unittest.mock import patch

from core.view import ConsoleView, DesktopView, IACEView


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


class TestDesktopView(unittest.TestCase):
    """Test cases for the DesktopView class."""

    @classmethod
    def setUpClass(cls):
        """Set up resources before any tests are run.

        This method is called once before any test methods are executed.
        It creates a DesktopView instance for all tests.
        """
        cls.desktop_view = DesktopView()
        cls.desktop_view.root.withdraw()  # Hide the window for testing

    @classmethod
    def tearDownClass(cls):
        """Clean up resources after all tests have run.

        This method is called once after all test methods have been executed.
        It destroys the GUI root window to prevent resource leaks.
        """
        try:
            cls.desktop_view.root.update_idletasks()
            cls.desktop_view.close()
        except tk.TclError:
            # If the window is already closed, ignore the error
            pass

    def setUp(self):
        """Reset the DesktopView state before each test."""
        self.desktop_view.clear_chat_history()
        self.desktop_view.reset_input()

    def assertMessageInHistory(self, message):
        """Helper method to assert a message is in the chat history."""
        chat_history = self.desktop_view.get_chat_history()
        self.assertIn(
            message, chat_history, f"Message '{message}' not found in chat history."
        )

    def test_desktop_view_implements_iaceview(self):
        """Test that DesktopView correctly implements the IACEView Protocol."""
        self.assertIsInstance(self.desktop_view, IACEView)

    def test_display_message(self):
        """Test that display_message adds the message to the window."""
        sender1 = "ACE"
        message1 = "Hello, how can I help?"
        self.desktop_view.display_message(sender1, message1)
        self.assertMessageInHistory(f"{sender1}: {message1}")

        sender2 = "YOU"
        message2 = "I need assistance."
        self.desktop_view.display_message(sender2, message2)
        self.assertMessageInHistory(f"{sender2}: {message2}")

        messages = "\n\n".join(self.desktop_view.get_chat_history())
        self.assertEqual(
            messages.strip(), f"{sender1}: {message1}\n\n{sender2}: {message2}"
        )

    def test_get_user_input(self):
        """Test that get_user_input retrieves user input from the input entry."""
        test_input = "Testing user input"
        self.desktop_view.input_entry.insert(0, test_input)
        user_input = self.desktop_view.get_user_input("Ask ACE: ")
        self.assertEqual(user_input, test_input)

    def test_show_special_messages(self):
        """Test that show_error and show_info display messages in the chat."""
        cases = [
            (
                "show_error",
                "[ERROR] Database connection failed.",
                "Database connection failed.",
            ),
            ("show_info", "[INFO] Application starting...", "Application starting..."),
        ]
        for method, expected, msg in cases:
            # Clear history for each case to test individually
            self.desktop_view.clear_chat_history()
            getattr(self.desktop_view, method)(msg)
            self.assertMessageInHistory(expected)


if __name__ == "__main__":
    unittest.main()
