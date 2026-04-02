""" "tests.views.test_console: Test the ConsoleView's ability to display messages and receive user input,
adhering to the expected interface defined by the ViewProtocol."""

import unittest
from unittest.mock import Mock

from core.adapters.protocols import IOAdapterProtocol
from core.views import ConsoleView
from core.views.protocols import Sender


class TestConsoleView(unittest.IsolatedAsyncioTestCase):
    """Test the ConsoleView's ability to display messages and receive user input."""

    async def asyncSetUp(self):
        """Set up common test components."""
        self.mock_io = Mock(spec=IOAdapterProtocol)
        self.view = ConsoleView(io_adapter=self.mock_io)

    async def test_start_loop_emits_signal(self):
        """Verify that input triggers the on_user_input signal."""
        # ARRANGE: Create mock handler and connect to the view's on_user_input signal
        mock_handler = Mock()
        self.view.events.on_user_input.connect(mock_handler)
        self.mock_io.get_input.return_value = "Hello ACE"

        self.view.events.on_user_input.connect(lambda _: self.view.stop())

        # ACT: Simulate the start loop
        await self.view.start()

        # ASSERT: Ensure the handler was called with the expected input and the adapter
        # was called to get user input
        mock_handler.assert_called_once_with("Hello ACE")
        self.mock_io.get_input.assert_called_once()

    async def test_stop_breaks_loop(self):
        """Verify that `stop()` correctly terminates the `start()` loop immediately."""
        # ARRANGE: Stop the view before starting to ensure it doesn't enter the loop
        self.view.stop()

        # ACT: Simulate the start loop
        await self.view.start()

        # ASSERT: Ensure the adapter's get_input method was never called, confirming
        # the loop was not entered
        self.mock_io.get_input.assert_not_called()

    async def test_get_input_delegates_to_io_adapter(self):
        """Verify that `get_user_input()` correctly delegates to the IO adapter."""
        # ARRANGE: Set up the mock IO adapter to return a specific input
        expected_input = "Test input"
        self.mock_io.get_input.return_value = expected_input

        # ACT: Call the view's get_user_input method
        result = self.view.get_user_input("Prompt: ")

        # ASSERT: Ensure the result matches the expected input and the adapter's
        # get_input method was called with the correct prompt
        self.assertEqual(result, expected_input)
        self.mock_io.get_input.assert_called_once_with("Prompt: ")

    async def test_display_message_delegates_to_io_adapter(self):
        """Verify that `display_message()` correctly delegates to the IO adapter."""
        # ARRANGE: Create a message to display
        message = "Hello, World!"

        # ACT: Call the view's display_message method
        self.view.display_message(Sender.INFO, message)

        # ASSERT: Ensure the adapter's display_output method was called with the
        # correct message and sender
        self.mock_io.display_output.assert_called_once_with(message, sender=Sender.INFO)

    async def test_show_error_delegates_to_io_adapter(self):
        """Verify that `show_error()` correctly delegates to the IO adapter."""
        # ARRANGE: Create an error message to display
        error_message = "An error occurred!"

        # ACT: Call the view's show_error method
        self.view.show_error(error_message)

        # ASSERT: Ensure the adapter's display_output method was called with the
        # correct error message (assuming show_error uses display_output for simplicity)
        self.mock_io.display_output.assert_called_once_with(f"ERROR: {error_message}")

    async def test_show_loading_placeholder(self):
        """Verify that `show_loading()` starts and stops the loading indicator correctly."""
        # ARRANGE: Create a mock function to execute during loading
        mock_function = Mock()

        # ACT: Call the view's show_loading method
        await self.view.show_loading("Loading data", mock_function)

        # ASSERT: Ensure the adapter's start_loading_indicator and stop_loading_indicator
        # methods were called with the correct message
        self.mock_io.start_loading_indicator.assert_called_once_with("Loading data")
        mock_function.assert_called_once()
        self.mock_io.stop_loading_indicator.assert_called_once()


if __name__ == "__main__":
    unittest.main()
