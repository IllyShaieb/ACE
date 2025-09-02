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
        # Suppress rich's output during tests for cleaner test results
        self.console_view.console.file = io.StringIO()

    def test_console_view_implements_iaceview(self):
        """Test that ConsoleView correctly implements the IACEView Protocol."""
        # This uses the @runtime_checkable decorator on IACEView
        self.assertTrue(isinstance(self.console_view, IACEView))

    def test_display_message(self):
        """Test that display_message prints the message content."""
        sender = "ACE"
        message = "Hello, how can I help?"
        self.console_view.display_message(sender, message)
        assert isinstance(self.console_view.console.file, io.StringIO)
        output = self.console_view.console.file.getvalue()
        self.assertIn(sender, output)
        self.assertIn(message, output)

    @patch("rich.console.Console.input", return_value="test user input")
    def test_get_user_input(self, mock_rich_input):
        """Test that get_user_input correctly captures and strips user input."""
        prompt = "Enter your command: "
        user_input = self.console_view.get_user_input(prompt)

        # Check that the input was captured correctly
        self.assertEqual(user_input, "test user input")

        # Check that rich's input was called
        mock_rich_input.assert_called_once()

        # Test with leading/trailing whitespace
        mock_rich_input.return_value = "  another input  "
        user_input = self.console_view.get_user_input("Prompt 2: ")
        self.assertEqual(user_input, "another input")

    def test_show_error(self):
        """Test that show_error prints the error message."""
        error_message = "Database connection failed."
        self.console_view.display_message("ERROR", error_message)
        assert isinstance(self.console_view.console.file, io.StringIO)
        output = self.console_view.console.file.getvalue()
        self.assertIn("ERROR", output)
        self.assertIn(error_message, output)

    def test_show_info(self):
        """Test that show_info prints the correct informational message."""
        info_message = "Application starting..."
        self.console_view.display_message("INFO", info_message)
        assert isinstance(self.console_view.console.file, io.StringIO)
        output = self.console_view.console.file.getvalue()
        self.assertIn("INFO", output)
        self.assertIn(info_message, output)


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
        self.assertTrue(isinstance(self.desktop_view, IACEView))

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
                "ERROR",
                "[ERROR] Database connection failed.",
                "Database connection failed.",
            ),
            (
                "INFO",
                "[INFO] Application starting...",
                "Application starting...",
            ),
        ]
        for sender, expected, msg in cases:
            # Clear history for each case to test individually
            self.desktop_view.clear_chat_history()
            self.desktop_view.display_message(sender, msg)
            self.assertMessageInHistory(expected)

    def test_display_conversation_history(self):
        """Test that the conversation history sidebar is populated correctly."""
        conversations = [
            (1, "2025-07-20T10:00:00"),
            (2, "2025-07-21T11:00:00"),
        ]
        self.desktop_view.display_conversations(conversations)

        # Expect a button for each conversation
        history_buttons = self.desktop_view.get_conversation_history()
        self.assertEqual(len(history_buttons), len(conversations))


if __name__ == "__main__":
    unittest.main()
