"""test_adapters.py: Ensure that the adapters are correctly implemented and can be
called as expected."""

import unittest
import uuid
from unittest.mock import MagicMock, patch

import requests

from core import adapters
from core.protocols import DatabaseServiceProtocol, Sender

##################################################################################
#                                  VIEW ADAPTERS                                 #
##################################################################################


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


##################################################################################
#                                  SERVICES ADAPTERS                             #
##################################################################################


class TestRequestsHTTPAdapter(unittest.TestCase):
    """Test the RequestsHTTPAdapter's ability to make GET and POST requests using the
    'requests' library."""

    def setUp(self) -> None:
        """Set up common test components."""
        self.adapter = adapters.RequestsHTTPAdapter()
        self.test_url = "https://api.example.com/test"

    @patch("core.adapters.requests.get")
    def test_get_success(self, mock_get):
        """Test that the GET method makes a GET request using the 'requests' library."""
        # ARRANGE: Set up the mock response for the GET request
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        test_parameters = {"param1": "value1"}
        test_headers = {"Authorization": "Bearer testtoken"}

        # ACT: Call the GET method of the adapter
        result = self.adapter.get(
            self.test_url, params=test_parameters, headers=test_headers
        )

        # ASSERT: Verify that the GET request was made with the correct parameters
        mock_get.assert_called_once_with(
            self.test_url, params=test_parameters, headers=test_headers
        )
        self.assertEqual(result, {"key": "value"})

    @patch("core.adapters.requests.get")
    def test_get_failure(self, mock_get):
        """Test that the GET method raises an exception for HTTP errors."""
        # ARRANGE: Set up the mock to raise an HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.RequestException(
            "HTTP error"
        )
        mock_get.return_value = mock_response

        # ACT & ASSERT: Verify it gets translated to a RuntimeError
        with self.assertRaises(RuntimeError) as context:
            self.adapter.get(self.test_url)

        self.assertIn("HTTP GET failed", str(context.exception))

    @patch("core.adapters.requests.post")
    def test_post_success(self, mock_post):
        """Test that the POST method makes a POST request using the 'requests' library."""
        # ARRANGE: Set up the mock response and test data for the POST request
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_post.return_value = mock_response

        test_cases = [
            {
                "data": None,
                "json": {"key": "value"},
                "headers": None,
                "description": "POST request with JSON payload",
            },
            {
                "data": {"field": "value"},
                "json": None,
                "headers": {"Content-Type": "application/x-www-form-urlencoded"},
                "description": "POST request with form data",
            },
            {
                "data": None,
                "json": None,
                "headers": None,
                "description": "POST request with no data",
            },
            {
                "data": {"field": "value"},
                "json": {"key": "value"},
                "headers": {"Content-Type": "application/json"},
                "description": "POST request with both form data and JSON payload",
            },
        ]

        for case in test_cases:
            with self.subTest(case["description"]):
                # ACT: Call the POST method of the adapter
                result = self.adapter.post(
                    self.test_url,
                    data=case["data"],
                    json=case["json"],
                    headers=case["headers"],
                )

                # ASSERT: Verify that the POST request was made with the correct
                # parameters
                mock_post.assert_called_with(
                    self.test_url,
                    data=case["data"],
                    json=case["json"],
                    headers=case["headers"],
                )
                self.assertEqual(result, {"key": "value"})

    @patch("core.adapters.requests.post")
    def test_post_failure(self, mock_post):
        """Test that the POST method raises an exception for HTTP errors."""
        # ARRANGE: Set up the mock to raise an HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.RequestException(
            "HTTP error"
        )
        mock_post.return_value = mock_response

        # ACT & ASSERT: Verify that an exception is raised when calling the POST method
        with self.assertRaises(RuntimeError) as context:
            self.adapter.post(self.test_url)

        self.assertIn("HTTP POST failed", str(context.exception))


#################################################################################
#                                 STORAGE ADAPTERS                              #
#################################################################################


class TestDatabaseConversationStorageAdapter(unittest.TestCase):
    """Test the DatabaseConversationStorageAdapter's ability to handle sessions and messages using a
    database service."""

    def setUp(self) -> None:
        self.maxDiff = None  # Allow full diff output for assertion failures

    def test_initialise_adapter(self):
        """Test that the DatabaseConversationStorageAdapter initialises the database and creates necessary tables."""
        # ARRANGE: Create an instance of the DatabaseConversationStorageAdapter with a mock database service
        mock_database_service = MagicMock(spec=DatabaseServiceProtocol)
        expected_config = {
            "sessions": {
                "session_id": "TEXT PRIMARY KEY",
                "title": "TEXT",
                "created_at": "TIMESTAMP",
                "updated_at": "TIMESTAMP",
            },
            "messages": {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "session_id": "TEXT",
                "timestamp": "TIMESTAMP",
                "sender": "TEXT",
                "content": "TEXT",
            },
        }

        # ACT: Initialise the DatabaseConversationStorageAdapter
        _ = adapters.DatabaseConversationStorageAdapter(
            database_service=mock_database_service
        )

        # ASSERT: Verify that the database service creates the necessary tables for conversations and messages
        for table_name, columns in expected_config.items():
            with self.subTest(
                table=table_name,
                msg=f"Table '{table_name}' should be created with the correct columns",
            ):
                mock_database_service.create_table.assert_any_call(
                    {
                        "table_name": table_name,
                        "columns": columns,
                    }
                )

    @patch("core.adapters.uuid.uuid4")
    @patch("core.adapters.datetime")
    def test_create_session(self, mock_datetime, mock_uuid4):
        """Test that the create_session method creates a new session and returns its unique identifier."""
        # ARRANGE: Create an instance of the DatabaseConversationStorageAdapter with a mock database service
        mock_database_service = MagicMock(spec=DatabaseServiceProtocol)
        adapter = adapters.DatabaseConversationStorageAdapter(
            database_service=mock_database_service
        )

        mock_datetime.now.return_value.strftime.return_value = "2026-03-12 12:00:00"
        mock_uuid4.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")

        test_cases = [
            {"title": "Test Session", "description": "Create session with title"},
            {"title": None, "description": "Create session without title"},
        ]

        for case in test_cases:
            with self.subTest(case["description"]):
                # ACT: Call the create_session method of the adapter
                session_id = adapter.create_session(title=case["title"])

                # ASSERT: Verify that the string returned by the method matches the UUID that was passed
                # into the insert call
                self.assertIsInstance(session_id, str)
                mock_database_service.insert.assert_any_call(
                    table="sessions",
                    data={
                        "session_id": session_id,
                        "title": case["title"] or "New Conversation",
                        "created_at": "2026-03-12 12:00:00",
                        "updated_at": "2026-03-12 12:00:00",
                    },
                )

    @patch("core.adapters.datetime")
    def test_save_message(self, mock_datetime):
        """Test that the save_message method saves a message to the conversation history for a given session."""
        # ARRANGE: Create an instance of the DatabaseConversationStorageAdapter with a mock database service
        mock_database_service = MagicMock(spec=DatabaseServiceProtocol)
        adapter = adapters.DatabaseConversationStorageAdapter(
            database_service=mock_database_service
        )

        test_session_id = "test-session-id"
        mock_datetime.now.return_value.strftime.return_value = "2026-03-12 12:00:00"
        test_role = "user"
        test_content = "Hello, this is a test message."

        # ACT: Call the save_message method of the adapter
        adapter.save_message(
            session_id=test_session_id, role=test_role, content=test_content
        )

        # ASSERT: Verify that the database service's insert method was called with the correct parameters
        # to save the message and the session updated_at timestamp was updated
        mock_database_service.insert.assert_called_with(
            table="messages",
            data={
                "session_id": test_session_id,
                "timestamp": "2026-03-12 12:00:00",
                "sender": test_role,
                "content": test_content,
            },
        )
        mock_database_service.update.assert_called_with(
            table="sessions",
            updates={"updated_at": "2026-03-12 12:00:00"},
            conditions={"session_id": test_session_id},
        )

    @patch("core.adapters.datetime")
    def test_get_session_messages(self, mock_datetime):
        """Test that the get_session_messages method retrieves the conversation history for a given session."""
        # ARRANGE: Create an instance of the DatabaseConversationStorageAdapter with a mock database service
        mock_database_service = MagicMock(spec=DatabaseServiceProtocol)
        adapter = adapters.DatabaseConversationStorageAdapter(
            database_service=mock_database_service
        )

        mock_datetime.now.return_value.strftime.side_effect = [
            "2026-03-12 12:00:00",
            "2026-03-12 12:01:00",
        ]

        test_session_id = "test-session-id"
        expected_messages = [
            {
                "session_id": test_session_id,
                "timestamp": "2026-03-12 12:00:00",
                "sender": "USER",
                "content": "Hello, this is a test message.",
            },
            {
                "session_id": test_session_id,
                "timestamp": "2026-03-12 12:01:00",
                "sender": "ACE",
                "content": "Hi! This is a response from ACE.",
            },
        ]

        mock_database_service.select.return_value = expected_messages

        # ACT: Call the get_session_messages method of the adapter
        messages = adapter.get_session_messages(session_id=test_session_id)

        # ASSERT: Verify that the database service's select method was called with the correct parameters
        # to retrieve messages for the session and that the returned messages match the expected messages
        mock_database_service.select.assert_called_with(
            table="messages",
            headers=["session_id", "timestamp", "sender", "content"],
            conditions={"session_id": test_session_id},
        )
        self.assertEqual(messages, expected_messages)

    @patch("core.adapters.datetime")
    def test_get_recent_sessions(self, mock_datetime):
        """Test that the get_recent_sessions method retrieves a list of recent conversation sessions."""
        # ARRANGE: Create an instance of the DatabaseConversationStorageAdapter with a mock database service
        mock_database_service = MagicMock(spec=DatabaseServiceProtocol)
        adapter = adapters.DatabaseConversationStorageAdapter(
            database_service=mock_database_service
        )

        mock_sessions_list = [
            {
                "session_id": "session-1",
                "title": "First Session",
                "created_at": "2026-03-12 12:00:00",
                "updated_at": "2026-03-12 12:30:00",
            },
            {
                "session_id": "session-2",
                "title": "Second Session",
                "created_at": "2026-03-12 13:00:00",
                "updated_at": "2026-03-12 13:30:00",
            },
        ]

        mock_database_service.select.return_value = mock_sessions_list

        test_cases = [
            {
                "description": "Get recent sessions with no limit",
                "limit": None,
                "expected_sessions": [
                    {
                        "session_id": "session-1",
                        "title": "First Session",
                        "created_at": "2026-03-12 12:00:00",
                        "updated_at": "2026-03-12 12:30:00",
                    },
                    {
                        "session_id": "session-2",
                        "title": "Second Session",
                        "created_at": "2026-03-12 13:00:00",
                        "updated_at": "2026-03-12 13:30:00",
                    },
                ],
            },
            {
                "description": "Get recent sessions with a limit of 1",
                "limit": 1,
                "expected_sessions": [
                    {
                        "session_id": "session-2",
                        "title": "Second Session",
                        "created_at": "2026-03-12 13:00:00",
                        "updated_at": "2026-03-12 13:30:00",
                    }
                ],
            },
            {
                "description": "Get recent sessions with a limit of 0 (should return all)",
                "limit": 0,
                "expected_sessions": [
                    {
                        "session_id": "session-1",
                        "title": "First Session",
                        "created_at": "2026-03-12 12:00:00",
                        "updated_at": "2026-03-12 12:30:00",
                    },
                    {
                        "session_id": "session-2",
                        "title": "Second Session",
                        "created_at": "2026-03-12 13:00:00",
                        "updated_at": "2026-03-12 13:30:00",
                    },
                ],
            },
            {
                "description": "Get recent sessions with a limit greater than the number of sessions (should return all)",
                "limit": 10,
                "expected_sessions": [
                    {
                        "session_id": "session-1",
                        "title": "First Session",
                        "created_at": "2026-03-12 12:00:00",
                        "updated_at": "2026-03-12 12:30:00",
                    },
                    {
                        "session_id": "session-2",
                        "title": "Second Session",
                        "created_at": "2026-03-12 13:00:00",
                        "updated_at": "2026-03-12 13:30:00",
                    },
                ],
            },
            {
                "description": "Get recent sessions with a negative limit (should return all)",
                "limit": -1,
                "expected_sessions": [
                    {
                        "session_id": "session-1",
                        "title": "First Session",
                        "created_at": "2026-03-12 12:00:00",
                        "updated_at": "2026-03-12 12:30:00",
                    },
                    {
                        "session_id": "session-2",
                        "title": "Second Session",
                        "created_at": "2026-03-12 13:00:00",
                        "updated_at": "2026-03-12 13:30:00",
                    },
                ],
            },
        ]

        for case in test_cases:
            with self.subTest(case["description"]):
                # ACT: Call the get_recent_sessions method of the adapter
                sessions = adapter.get_recent_sessions(limit=case["limit"])

                # ASSERT: Verify that the database service's select method was called with the correct parameters
                # to retrieve recent sessions and that the returned sessions match the expected sessions
                mock_database_service.select.assert_called_with(
                    table="sessions",
                    headers=["session_id", "title", "created_at", "updated_at"],
                )
                self.assertEqual(
                    sessions,
                    sorted(
                        case["expected_sessions"],
                        key=lambda x: x["updated_at"],
                        reverse=True,
                    ),
                )

    @patch("core.adapters.datetime")
    def test_update_session_title(self, mock_datetime):
        """Test that the update_session_title method updates the title of a conversation session."""
        # ARRANGE: Create an instance of the DatabaseConversationStorageAdapter with a mock database service
        mock_database_service = MagicMock(spec=DatabaseServiceProtocol)
        adapter = adapters.DatabaseConversationStorageAdapter(
            database_service=mock_database_service
        )

        mock_datetime.now.return_value.strftime.return_value = "2026-03-12 12:00:00"

        test_cases = [
            {
                "session_id": "test-session-id",
                "new_title": "Updated Session Title",
                "expected_title": "Updated Session Title",
                "description": "Update session title with a valid session ID and new title",
            },
            {
                "session_id": "test-session-id",
                "new_title": "",
                "expected_title": "New Conversation",
                "description": "Update session title to an empty string (not allowed)",
            },
            {
                "session_id": "test-session-id",
                "new_title": None,
                "expected_title": "New Conversation",
                "description": "Update session title to None (should be handled gracefully)",
            },
        ]

        for case in test_cases:
            with self.subTest(case["description"]):
                # ACT: Call the update_session_title method of the adapter
                adapter.update_session_title(
                    session_id=case["session_id"], title=case["new_title"]
                )

                # ASSERT: Verify that the database service's update method was called with the correct parameters
                # to update the session title
                mock_database_service.update.assert_any_call(
                    table="sessions",
                    updates={
                        "title": case["expected_title"],
                        "updated_at": "2026-03-12 12:00:00",
                    },
                    conditions={"session_id": case["session_id"]},
                )

    def test_delete_session(self):
        """Test that the delete_session method deletes a conversation session and its associated messages."""
        # ARRANGE: Create an instance of the DatabaseConversationStorageAdapter with a mock database service
        mock_database_service = MagicMock(spec=DatabaseServiceProtocol)
        adapter = adapters.DatabaseConversationStorageAdapter(
            database_service=mock_database_service
        )

        test_session_id = "test-session-id"

        # ACT: Call the delete_session method of the adapter
        adapter.delete_session(session_id=test_session_id)

        # ASSERT: Verify that the database service's delete method was called with the correct parameters
        # to delete the session and its associated messages
        mock_database_service.delete.assert_any_call(
            table="sessions", conditions={"session_id": test_session_id}
        )
        mock_database_service.delete.assert_any_call(
            table="messages", conditions={"session_id": test_session_id}
        )


if __name__ == "__main__":
    unittest.main()
