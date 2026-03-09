"""tests.test_presenters: Ensure that the presenter layer correctly mediates between the model and view, handling user input and updating the view accordingly. This includes testing the logic for processing user commands, managing state transitions, and ensuring that the presenter correctly updates the view based on changes in the model."""

import unittest
from unittest.mock import AsyncMock, Mock

from core.presenters import ConsolePresenter
from core.protocols import ModelProtocol, Sender, ViewProtocol


class TestConsolePresenter(unittest.IsolatedAsyncioTestCase):
    """Test the ConsolePresenter's ability to process user input and update the view accordingly."""

    async def asyncSetUp(self) -> None:
        """Set up common test components."""
        self.mock_model = AsyncMock(spec=ModelProtocol)
        self.mock_view = Mock(spec=ViewProtocol)
        self.presenter = ConsolePresenter(model=self.mock_model, view=self.mock_view)

    async def test_initialisation_connects_signal(self):
        """Verify that the presenter connects to the view's user input events during initialisation."""
        # ASSERT: Verify event connection
        self.mock_view.events.on_user_input.connect.assert_called_once_with(
            self.presenter.handle_user_input
        )

    async def test_run_displays_welcome_message(self):
        """Verify that `run()` displays the welcome message if provided."""
        # ARRANGE: Define a welcome message
        welcome_message = "Welcome to ACE!"
        presenter_with_welcome = ConsolePresenter(
            model=self.mock_model, view=self.mock_view, welcome_message=welcome_message
        )

        # ACT: Run the presenter
        await presenter_with_welcome.run()

        # ASSERT: Verify the welcome message is displayed
        self.mock_view.display_message.assert_called_once_with(
            Sender.INFO, welcome_message
        )

    async def test_handle_user_input_success_flow(self):
        """Verify that `handle_user_input()` processes input and updates the view correctly."""
        # ARRANGE: Define a sample user input and expected model response
        user_input = "What is the current date and time?"
        model_response = (
            "The current date and time is Monday, January 01, 2026 at 12:00 PM."
        )
        self.mock_view.show_loading = AsyncMock(return_value=model_response)

        # ACT: Handle the user input
        await self.presenter.handle_user_input(user_input)

        # ASSERT: Verify the model processed the query and the view was updated

        # 1. Check that the view's `show_loading()` was called with the correct user input
        self.mock_view.show_loading.assert_awaited_once_with(
            "Thinking...",
            self.mock_model.process_query,
            query=user_input,
        )

        # 2. Check that the view's `display_message()` was called with the correct sender and response
        self.mock_view.display_message.assert_called_once_with(
            Sender.ACE, model_response
        )

    async def test_handle_user_input_exit(self):
        """Verify that `handle_user_input()` stops the view when the exit command is received."""
        # ARRANGE: Define the exit command
        exit_command = "exit"

        # ACT: Handle the exit command
        await self.presenter.handle_user_input(exit_command)

        # ASSERT: Verify that the view's `stop()` method was called and `process_query()` was not
        self.mock_view.stop.assert_called_once()
        self.mock_model.process_query.assert_not_called()

    async def test_handle_user_input_empty_string(self):
        """Verify that `handle_user_input()` ignores empty input."""
        # ARRANGE: Define an empty user input
        empty_input = "   "  # Input with only whitespace

        # ACT: Handle the empty user input
        await self.presenter.handle_user_input(empty_input)

        # ASSERT: Verify that the model's `process_query()` was not called and the view was not updated
        self.mock_model.process_query.assert_not_called()
        self.mock_view.display_message.assert_not_called()


if __name__ == "__main__":
    unittest.main()
