"""test_presenter.py: Unit tests for the ACE Presenter."""

import unittest
from unittest.mock import Mock, call, patch
import os
from datetime import datetime

from core.presenter import (
    USER_ID,
    ACEPresenter,
    ACE_ID,
    EXIT_COMMAND,
    WELCOME_MESSAGE,
    GOODBYE_MESSAGE,
    UNKNOWN_ACTION_MESSAGE,
)
from core.view import IACEView

TEST_ACE_DATABASE = "data/test_ace.db"


class TestACEPresenter(unittest.TestCase):
    """
    Test cases for the ACEPresenter class, focusing on verifying
    interactions between the presenter, model, and view.
    """

    def setUp(self):
        """Set up for each test case."""
        # Create mock objects for Model and View
        self.mock_model = Mock()
        self.mock_view = Mock(spec=IACEView)

        # Instantiate the Presenter with the mock objects
        self.presenter = ACEPresenter(model=self.mock_model, view=self.mock_view)

        # Ensure the test database does not exist before each test
        if os.path.exists(TEST_ACE_DATABASE):
            os.remove(TEST_ACE_DATABASE)

        # Patch the database path for all tests in this class to use the test db
        self.patcher_db_path = patch("core.presenter.ACE_DATABASE", TEST_ACE_DATABASE)
        self.patcher_db_path.start()

        # Patch datetime.now to control timestamps for consistent assertions
        self.mock_datetime_now = patch("core.presenter.datetime")
        self.mock_dt = self.mock_datetime_now.start()
        self.mock_dt.now.return_value = datetime(2025, 7, 21, 10, 0, 0)

    def tearDown(self):
        """Tear down after each test case."""
        self.patcher_db_path.stop()
        if os.path.exists(TEST_ACE_DATABASE):
            os.remove(TEST_ACE_DATABASE)

    def test_presenter_initialisation(self):
        """Test that the presenter is initialised correctly."""
        self.assertIs(self.presenter.model, self.mock_model)
        self.assertIs(self.presenter.view, self.mock_view)
        self.assertIsNone(self.presenter.chat_id)

    @patch("core.presenter.create_database")
    @patch("core.presenter.start_conversation", return_value="id_123")
    @patch("core.presenter.add_message")
    def test_run_application_success(
        self, mock_add_message, mock_start_conversation, mock_create_database
    ):
        """
        Test successful application startup and initial messages.

        Verifies that the database is created, a conversation is started,
        the welcome and goodbye messages are displayed, and the messages
        are logged correctly.
        """
        # Arrange
        self.mock_view.get_user_input.side_effect = [EXIT_COMMAND]

        # Act
        self.presenter.run()

        # Assert
        mock_create_database.assert_called_once_with(TEST_ACE_DATABASE)
        mock_start_conversation.assert_called_once_with(TEST_ACE_DATABASE)
        self.assertEqual(self.presenter.chat_id, "id_123")
        self.mock_view.show_info.assert_called()

        self.mock_view.display_message.assert_has_calls(
            [
                call(ACE_ID, WELCOME_MESSAGE),
                call(ACE_ID, GOODBYE_MESSAGE),
            ],
            any_order=False,
        )

        mock_add_message.assert_has_calls(
            [
                call(TEST_ACE_DATABASE, "id_123", ACE_ID, WELCOME_MESSAGE),
                call(TEST_ACE_DATABASE, "id_123", USER_ID, EXIT_COMMAND),
                call(TEST_ACE_DATABASE, "id_123", ACE_ID, GOODBYE_MESSAGE),
            ],
            any_order=False,
        )

    @patch("core.presenter.create_database", side_effect=Exception("DB Error"))
    def test_run_application_db_failure(self, mock_create_database):
        """
        Test application startup failure due to database error.

        Verifies that the application handles a database creation error
        gracefully by showing an error message and exiting.
        """
        # Arrange
        self.mock_view.get_user_input.side_effect = [EXIT_COMMAND]

        # Act
        self.presenter.run()

        # Assert
        mock_create_database.assert_called_once_with(TEST_ACE_DATABASE)
        self.mock_view.show_error.assert_called_once_with(
            "Failed to initialise database: DB Error"
        )

        expected_info_calls = [
            call("2025-07-21 10:00:00 | Initialising ACE"),
            call("[INFO] ACE cannot start without a functional database. Exiting."),
        ]
        self.mock_view.show_info.assert_has_calls(expected_info_calls, any_order=False)

        self.mock_view.display_message.assert_not_called()
        self.assertIsNone(self.presenter.chat_id)

    @patch("core.presenter.create_database")
    @patch("core.presenter.start_conversation", return_value="id_789")
    @patch("core.presenter.add_message")
    def test_single_action_query(
        self, mock_add_message, mock_start_conversation, mock_create_database
    ):
        """
        Test a query that results in a single action and response.

        Verifies that the presenter correctly processes a single action
        from the model and displays the appropriate response.
        """
        # Arrange
        user_query = "who are you?"
        self.mock_model.return_value = ["IDENTIFY"]
        self.mock_view.get_user_input.side_effect = [user_query, EXIT_COMMAND]
        expected_response = "I am ACE, your personal assistant."

        # Act
        self.presenter.run()

        # Assert
        self.mock_model.assert_called_once_with(user_query)
        self.mock_view.display_message.assert_has_calls(
            [
                call(ACE_ID, WELCOME_MESSAGE),
                call(ACE_ID, expected_response),
                call(ACE_ID, GOODBYE_MESSAGE),
            ]
        )
        mock_add_message.assert_has_calls(
            [
                call(TEST_ACE_DATABASE, "id_789", ACE_ID, WELCOME_MESSAGE),
                call(TEST_ACE_DATABASE, "id_789", USER_ID, user_query),
                call(TEST_ACE_DATABASE, "id_789", ACE_ID, expected_response),
                call(TEST_ACE_DATABASE, "id_789", USER_ID, EXIT_COMMAND),
                call(TEST_ACE_DATABASE, "id_789", ACE_ID, GOODBYE_MESSAGE),
            ],
            any_order=False,
        )

    @patch("core.presenter.create_database")
    @patch("core.presenter.start_conversation", return_value="id_999")
    @patch("core.presenter.add_message")
    def test_multi_action_query(
        self, mock_add_message, mock_start_conversation, mock_create_database
    ):
        """
        Test a query that results in multiple actions and responses.

        Verifies that the presenter correctly processes multiple actions
        and displays the combined response in the correct order.
        """
        # Arrange
        user_query = "who are you and who is your creator?"
        self.mock_model.return_value = ["IDENTIFY", "CREATOR"]
        self.mock_view.get_user_input.side_effect = [user_query, EXIT_COMMAND]

        # Expected responses
        identify_response = "I am ACE, your personal assistant."
        creator_response = "I was created by Illy Shaieb."
        combined_response = f"{identify_response} {creator_response}"

        # Act
        self.presenter.run()

        # Assert
        self.mock_model.assert_called_once_with(user_query)
        self.mock_view.display_message.assert_has_calls(
            [
                call(ACE_ID, WELCOME_MESSAGE),
                call(ACE_ID, combined_response),
                call(ACE_ID, GOODBYE_MESSAGE),
            ],
            any_order=False,
        )
        mock_add_message.assert_has_calls(
            [
                call(TEST_ACE_DATABASE, "id_999", ACE_ID, WELCOME_MESSAGE),
                call(TEST_ACE_DATABASE, "id_999", USER_ID, user_query),
                call(TEST_ACE_DATABASE, "id_999", ACE_ID, combined_response),
                call(TEST_ACE_DATABASE, "id_999", USER_ID, EXIT_COMMAND),
                call(TEST_ACE_DATABASE, "id_999", ACE_ID, GOODBYE_MESSAGE),
            ],
            any_order=False,
        )

    @patch("core.presenter.create_database")
    @patch("core.presenter.start_conversation", return_value="id_err")
    @patch("core.presenter.add_message")
    def test_unrecognized_action(
        self, mock_add_message, mock_start_conversation, mock_create_database
    ):
        """
        Test that the presenter handles an unknown action from the model.

        Verifies that the presenter displays an appropriate message
        when the model returns an action that is not recognised.
        """
        # Arrange
        user_query = "do a backflip"
        self.mock_model.return_value = ["BACKFLIP"]
        self.mock_view.get_user_input.side_effect = [user_query, EXIT_COMMAND]

        # Act
        self.presenter.run()

        # Assert
        self.mock_view.display_message.assert_has_calls(
            [
                call(ACE_ID, WELCOME_MESSAGE),
                call(ACE_ID, UNKNOWN_ACTION_MESSAGE),
                call(ACE_ID, GOODBYE_MESSAGE),
            ]
        )

    @patch("core.presenter.create_database")
    @patch("core.presenter.start_conversation", return_value="id_1000")
    @patch("core.presenter.add_message")
    def test_multi_action_query_respects_response_order(
        self, mock_add_message, mock_start_conversation, mock_create_database
    ):
        """
        Test that combined responses for multiple actions respect query order.

        Verifies that the presenter processes multiple actions in the order
        they appear in the query and displays the combined response correctly.
        """
        # Arrange
        user_query = "who is your creator and who are you?"
        self.mock_model.return_value = ["CREATOR", "IDENTIFY"]
        self.mock_view.get_user_input.side_effect = [user_query, EXIT_COMMAND]

        # Expected responses
        identify_response = "I am ACE, your personal assistant."
        creator_response = "I was created by Illy Shaieb."
        combined_response = f"{creator_response} {identify_response}"

        # Act
        self.presenter.run()

        # Assert
        self.mock_model.assert_called_once_with(user_query)
        self.mock_view.display_message.assert_has_calls(
            [
                call(ACE_ID, WELCOME_MESSAGE),
                call(ACE_ID, combined_response),
                call(ACE_ID, GOODBYE_MESSAGE),
            ],
            any_order=False,
        )
        mock_add_message.assert_has_calls(
            [
                call(TEST_ACE_DATABASE, "id_1000", ACE_ID, WELCOME_MESSAGE),
                call(TEST_ACE_DATABASE, "id_1000", USER_ID, user_query),
                call(TEST_ACE_DATABASE, "id_1000", ACE_ID, combined_response),
                call(TEST_ACE_DATABASE, "id_1000", USER_ID, EXIT_COMMAND),
                call(TEST_ACE_DATABASE, "id_1000", ACE_ID, GOODBYE_MESSAGE),
            ],
            any_order=False,
        )


if __name__ == "__main__":
    unittest.main()
