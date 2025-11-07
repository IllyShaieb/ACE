"""test_presenter.py: Unit tests for the ACE Presenter."""

import os
import unittest
from datetime import datetime
from unittest.mock import Mock, call, patch

# Import database functions directly for setup
from core.database import create_database
from core.presenter import (
    ACE_ID,
    EMPTY_RESPONSE_MESSAGE,
    EXIT_COMMAND,
    USER_ID,
    WELCOME_MESSAGE,
    ConsolePresenter,
    DesktopPresenter,
)
from core.view import IACEView

# Use a dedicated test database
TEST_ACE_DATABASE = "data/test_ace.db"


class TestConsolePresenter(unittest.TestCase):
    """
    Test cases for the ConsolePresenter class, focusing on verifying
    interactions between the presenter, model, and view.
    """

    def setUp(self):
        """Set up for each test case."""
        self.patcher_db_path = patch("core.presenter.ACE_DATABASE", TEST_ACE_DATABASE)
        self.patcher_db_path.start()

        if os.path.exists(TEST_ACE_DATABASE):
            os.remove(TEST_ACE_DATABASE)
        create_database(TEST_ACE_DATABASE)

        self.mock_model = Mock()
        self.mock_view = Mock(spec=IACEView)
        self.presenter = ConsolePresenter(model=self.mock_model, view=self.mock_view)

        self.mock_datetime_now = patch("core.presenter.datetime")
        self.mock_dt = self.mock_datetime_now.start()
        self.mock_dt.now.return_value = datetime(2025, 7, 21, 10, 0, 0)
        self.mock_dt.strftime = datetime.strftime

        # Patch track_action to just call the function
        self.patcher_track_action = patch.object(
            self.mock_view, "track_action", side_effect=lambda f, *args: f()
        )
        self.patcher_track_action.start()

    def tearDown(self):
        """Tear down after each test case."""
        self.patcher_track_action.stop()
        self.mock_datetime_now.stop()
        self.patcher_db_path.stop()
        if os.path.exists(TEST_ACE_DATABASE):
            os.remove(TEST_ACE_DATABASE)

    def test_presenter_initialisation(self):
        """Test that the presenter is initialised correctly."""
        self.assertIs(self.presenter.model, self.mock_model)
        self.assertIs(self.presenter.view, self.mock_view)
        self.assertIsNone(self.presenter.chat_id)

    @patch("core.presenter.add_message")
    def test_run_application_success(self, mock_add_message):
        """Test successful application startup and a single interaction."""
        self.mock_view.get_user_input.side_effect = ["hello", EXIT_COMMAND]
        self.mock_model.return_value = "Hello to you too."

        # Act
        self.presenter.run()

        # Assert
        self.assertEqual(self.presenter.chat_id, 1)  # Chat was created

        # FIX 2: Removed call('YOU', 'exit') as it is not displayed
        self.mock_view.display_message.assert_has_calls(
            [
                call("INFO", "2025-07-21 10:00:00 | Initialising ACE"),
                call("INFO", "    Welcome to ACE! Type 'exit' to quit.\n\n"),
                call(ACE_ID, WELCOME_MESSAGE),
                call(USER_ID, "hello"),
                call(ACE_ID, "Hello to you too."),
                # "exit" is ingested but not displayed
                call("INFO", "2025-07-21 10:00:00 | Terminating ACE"),
            ],
            any_order=False,
        )

        mock_add_message.assert_has_calls(
            [
                call(TEST_ACE_DATABASE, 1, ACE_ID, WELCOME_MESSAGE),
                call(TEST_ACE_DATABASE, 1, USER_ID, "hello"),
                call(TEST_ACE_DATABASE, 1, ACE_ID, "Hello to you too."),
            ],
        )

    @patch("core.presenter.create_database", side_effect=Exception("DB Error"))
    def test_run_application_db_failure(self, mock_create_database):
        """Test application startup failure due to database error."""
        self.presenter.run()
        mock_create_database.assert_called_once_with(TEST_ACE_DATABASE)
        self.mock_view.display_message.assert_any_call(
            "ERROR", "Failed to initialise database: DB Error"
        )
        self.assertIsNone(self.presenter.chat_id)

    def test_unrecognised_action(self):
        """Test that the presenter handles an empty/unknown response from the model."""
        user_query = "gibberish"
        self.mock_model.return_value = ""
        self.mock_view.get_user_input.side_effect = [user_query, EXIT_COMMAND]

        self.presenter.run()
        self.mock_view.display_message.assert_any_call(ACE_ID, EMPTY_RESPONSE_MESSAGE)


class TestDesktopPresenter(unittest.TestCase):
    """Test cases for the DesktopPresenter class."""

    def setUp(self):
        """Set up for each test case."""
        self.patcher_db_path = patch("core.presenter.ACE_DATABASE", TEST_ACE_DATABASE)
        self.patcher_db_path.start()

        if os.path.exists(TEST_ACE_DATABASE):
            os.remove(TEST_ACE_DATABASE)
        create_database(TEST_ACE_DATABASE)

        self.mock_model = Mock()
        self.mock_view = Mock(spec=IACEView)
        self.presenter = DesktopPresenter(model=self.mock_model, view=self.mock_view)

        self.thread_patcher = patch("core.presenter.Thread", new=self._sync_thread)
        self.thread_patcher.start()

        self.mock_datetime_now = patch("core.presenter.datetime")
        self.mock_dt = self.mock_datetime_now.start()
        self.mock_dt.now.return_value = datetime(2025, 7, 21, 10, 0, 0)
        self.mock_dt.strftime = datetime.strftime

        # FIX 3: This patch is necessary to make the mock view execute the lambda
        # that calls the model.
        self.patcher_track_action = patch.object(
            self.mock_view, "track_action", side_effect=lambda f: f()
        )
        self.patcher_track_action.start()

        self.patcher_after = patch.object(
            self.mock_view, "after", side_effect=lambda ms, cb: cb()
        )
        self.patcher_after.start()

    def tearDown(self):
        """Tear down after each test case."""
        self.thread_patcher.stop()
        self.patcher_track_action.stop()  # Stop track_action patch
        self.mock_datetime_now.stop()
        self.patcher_after.stop()
        self.patcher_db_path.stop()
        if os.path.exists(TEST_ACE_DATABASE):
            os.remove(TEST_ACE_DATABASE)

    @staticmethod
    def _sync_thread(target, *args, **kwargs):
        """A fake Thread that runs the target synchronously."""
        thread_args = kwargs.get("args", ())
        thread_kwargs = kwargs.get("kwargs", {})
        target(*thread_args, **thread_kwargs)
        return Mock()

    def test_single_action_query(self):
        """Test a single query and response."""
        user_query = "who are you?"
        expected_response = "I am ACE."
        self.mock_model.return_value = expected_response

        self.presenter.start_new_conversation()
        self.assertIsNone(self.presenter.chat_id)

        # Act
        self.presenter.handle_user_input(user_query)

        # Assert
        self.assertEqual(self.presenter.chat_id, 1)

        # FIX 4: Assert that the model was called with the WELCOME_MESSAGE in history
        expected_history = [{"role": "model", "text": WELCOME_MESSAGE}]
        self.mock_model.assert_called_once_with(user_query, expected_history)

        self.mock_view.display_message.assert_has_calls(
            [call(USER_ID, user_query), call(ACE_ID, expected_response)]
        )
        self.mock_view.hide_typing_indicator.assert_called_once()

    def test_unrecognised_action(self):
        """Test an empty response from the model."""
        user_query = "gibberish"
        self.mock_model.return_value = ""  # Empty response

        self.presenter.start_new_conversation()

        # Act
        self.presenter.handle_user_input(user_query)

        # Assert
        self.assertEqual(self.presenter.chat_id, 1)

        # FIX 4: Assert that the model was called with the WELCOME_MESSAGE in history
        expected_history = [{"role": "model", "text": WELCOME_MESSAGE}]
        self.mock_model.assert_called_once_with(user_query, expected_history)

        self.mock_view.display_message.assert_has_calls(
            [call(USER_ID, user_query), call(ACE_ID, EMPTY_RESPONSE_MESSAGE)]
        )
        self.mock_view.hide_typing_indicator.assert_called_once()


if __name__ == "__main__":
    unittest.main()
