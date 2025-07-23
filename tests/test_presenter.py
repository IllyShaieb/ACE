"""test_presenter.py: Unit tests for the ACE Presenter."""

import unittest
from unittest.mock import ANY, Mock, call, patch
import os
from datetime import datetime

from core.presenter import USER_ID, ACEPresenter, ACE_ID, EXIT_COMMAND
from core.view import IACEView

TEST_ACE_DATABASE = "data/test_ace.db"
WELCOME_MESSAGE = "Hello! I am ACE, your personal assistant. How can I help you today?"
GOODBYE_MESSAGE = "Goodbye! It was a pleasure assisting you."


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
    @patch("core.presenter.start_conversation", return_value="id_456")
    @patch("core.presenter.add_message")
    def test_conversation_loop_exit_command(
        self, mock_add_message, mock_start_conversation, mock_create_database
    ):
        """
        Test that the conversation loop exits on 'exit' command.

        Verifies that the application exits the conversation loop when
        the user enters the 'exit' command.
        """
        # Arrange
        self.mock_view.get_user_input.side_effect = [EXIT_COMMAND]

        # Act
        self.presenter.run()

        # Assert
        self.mock_view.get_user_input.assert_called_once_with(f"{USER_ID}: ")
        self.mock_view.display_message.assert_called_with(ACE_ID, GOODBYE_MESSAGE)
        mock_add_message.assert_called_with(
            TEST_ACE_DATABASE, "id_456", ACE_ID, GOODBYE_MESSAGE
        )
        self.mock_model.assert_not_called()

    @patch("core.presenter.create_database")
    @patch("core.presenter.start_conversation", return_value="id_789")
    @patch("core.presenter.add_message")
    def test_conversation_loop_user_query_and_response(
        self, mock_add_message, mock_start_conversation, mock_create_database
    ):
        """
        Test a typical user query and ACE's response.

        Verifies that the application correctly handles a user query,
        calls the model to get a response, displays the response,
        and logs the interaction.
        """
        # Arrange
        user_query = "hello"
        model_response = "Hello there! How can I assist you today?"
        self.mock_view.get_user_input.side_effect = [user_query, EXIT_COMMAND]
        self.mock_model.return_value = model_response

        # Act
        self.presenter.run()

        # Assert
        self.mock_view.get_user_input.assert_has_calls(
            [call(f"{USER_ID}: "), call(f"{USER_ID}: ")]
        )
        self.mock_model.assert_called_once_with(user_query)

        self.mock_view.display_message.assert_has_calls(
            [
                call(ACE_ID, WELCOME_MESSAGE),
                call(ACE_ID, model_response),
                call(ACE_ID, GOODBYE_MESSAGE),
            ]
        )

        expected_add_message_calls = [
            call(TEST_ACE_DATABASE, "id_789", ACE_ID, WELCOME_MESSAGE),
            call(TEST_ACE_DATABASE, "id_789", USER_ID, user_query),
            call(TEST_ACE_DATABASE, "id_789", ACE_ID, model_response),
            call(TEST_ACE_DATABASE, "id_789", USER_ID, EXIT_COMMAND),
            call(TEST_ACE_DATABASE, "id_789", ACE_ID, GOODBYE_MESSAGE),
        ]
        mock_add_message.assert_has_calls(expected_add_message_calls, any_order=False)

    @patch("core.presenter.create_database")
    @patch("core.presenter.start_conversation", return_value="test_chat_id_error")
    @patch("core.presenter.add_message")
    def test_conversation_loop_general_error_handling(
        self, mock_add_message, mock_start_conversation, mock_create_database
    ):
        """
        Test that the conversation loop handles general exceptions gracefully.

        Simulates an error occurring during the conversation loop and
        verifies that the application handles it without crashing.
        """
        # Arrange
        first_query = "first query"
        second_query = "second query (will cause error)"
        model_response = "Response to first query"
        error_message = "Model Processing Error"

        self.mock_view.get_user_input.side_effect = [
            first_query,
            second_query,
            EXIT_COMMAND,
        ]
        self.mock_model.side_effect = [model_response, Exception(error_message)]

        # Act
        self.presenter.run()

        # Assert
        self.mock_view.show_error.assert_called_once()
        self.assertTrue(error_message in self.mock_view.show_error.call_args[0][0])

        self.mock_view.display_message.assert_has_calls(
            [
                call(ACE_ID, WELCOME_MESSAGE),
                call(ACE_ID, model_response),
                call(ACE_ID, GOODBYE_MESSAGE),
            ]
        )

        # Verify add_message calls, including the error logging
        logged_error_call = call(TEST_ACE_DATABASE, "test_chat_id_error", ACE_ID, ANY)
        self.assertIn(logged_error_call, mock_add_message.call_args_list)

        mock_add_message.assert_has_calls(
            [
                call(TEST_ACE_DATABASE, "test_chat_id_error", ACE_ID, WELCOME_MESSAGE),
                call(TEST_ACE_DATABASE, "test_chat_id_error", USER_ID, first_query),
                call(TEST_ACE_DATABASE, "test_chat_id_error", ACE_ID, model_response),
                call(TEST_ACE_DATABASE, "test_chat_id_error", USER_ID, second_query),
                call(TEST_ACE_DATABASE, "test_chat_id_error", ACE_ID, ANY),
                call(TEST_ACE_DATABASE, "test_chat_id_error", USER_ID, EXIT_COMMAND),
                call(TEST_ACE_DATABASE, "test_chat_id_error", ACE_ID, GOODBYE_MESSAGE),
            ],
            any_order=False,
        )


if __name__ == "__main__":
    unittest.main()
