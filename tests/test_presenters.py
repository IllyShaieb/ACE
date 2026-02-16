"""tests.test_presenters: Ensure that the presenter layer correctly mediates between the model and view, handling user input and updating the view accordingly. This includes testing the logic for processing user commands, managing state transitions, and ensuring that the presenter correctly updates the view based on changes in the model."""

import unittest
from unittest.mock import Mock

from core.presenters import ConsolePresenter
from core.protocols import ModelProtocol, Sender, ViewProtocol


class TestConsolePresenter(unittest.TestCase):
    """Test the ConsolePresenter's ability to process user input and update the view accordingly."""

    def test_initialisation(self):
        """Test that the presenter initializes correctly with the given model, view and connects
        view events to presenter methods."""

        # ARRANGE: Create mock model and view
        mock_model = Mock(spec=ModelProtocol)
        mock_view = Mock(spec=ViewProtocol)

        # ACT: Initialize the presenter
        presenter = ConsolePresenter(model=mock_model, view=mock_view)

        # ASSERT: Check that the view's events are connected
        self.assertIsNotNone(
            presenter.view.events,
            msg="Presenter should have access to the view's events",
        )

    def test_handle_user_input_updates_view_and_returns_none(self):
        """Ensure handle_user_input processes query through model and updates view
        without returning a value."""
        # ARRANGE: Create mock model, view and presenter
        mock_model = Mock(spec=ModelProtocol)
        mock_view = Mock(spec=ViewProtocol)

        expected_response = "model response"
        mock_model.process_query.return_value = expected_response

        presenter = ConsolePresenter(model=mock_model, view=mock_view)

        # ACT: Simulate user input
        user_input = "test command"
        result = presenter.handle_user_input(user_input)

        # ASSERT: Check that the model's process_query method was called with the
        # user input

        # 1. Ensure that the presenter is passive
        self.assertIsNone(
            result,
            msg="handle_user_input should not return any value, it should be passive",
        )

        # 2. Check model is called with the user input
        mock_model.process_query.assert_called_once_with(user_input)

        # 3. Check view was told to display the model's response
        mock_view.display_message.assert_called_once_with(Sender.ACE, expected_response)

    def test_run_method_displays_welcome_message(self):
        """Ensure that the run method displays a welcome message to the user."""
        # ARRANGE: Create mock model, view and presenter
        mock_model = Mock(spec=ModelProtocol)
        mock_view = Mock(spec=ViewProtocol)

        mock_view.get_user_input.side_effect = ["exit"]

        welcome_message = "Welcome to ACE!"

        presenter = ConsolePresenter(
            model=mock_model, view=mock_view, welcome_message=welcome_message
        )

        # ACT: Call the run method
        presenter.run()

        # ASSERT: Check that the view's display_message method was called with a welcome message
        # 1. Check that the view's start method was called
        mock_view.display_message.assert_any_call(Sender.INFO, welcome_message)

        # 2. Check that the view's start method was called
        mock_view.start.assert_called_once()


if __name__ == "__main__":
    unittest.main()
