import unittest
import uuid
from unittest.mock import MagicMock, patch

from core import adapters
from core.services.protocols import DatabaseServiceProtocol


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

    @patch("core.adapters.storage.uuid.uuid4")
    @patch("core.adapters.storage.datetime")
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

    @patch("core.adapters.storage.datetime")
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

    @patch("core.adapters.storage.datetime")
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

    @patch("core.adapters.storage.datetime")
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

    @patch("core.adapters.storage.datetime")
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


class TestDatabaseLogStorageAdapter(unittest.TestCase):
    """Test the DatabaseLogStorageAdapter's ability to log messages using a database service."""

    def setUp(self) -> None:
        self.maxDiff = None  # Allow full diff output for assertion failures

    def test_initialise_adapter(self):
        """Test that the DatabaseLogStorageAdapter initialises the database and creates necessary tables."""
        # ARRANGE: Create an instance of the DatabaseLogStorageAdapter with a mock database service
        mock_database_service = MagicMock(spec=DatabaseServiceProtocol)
        expected_config = {
            "logs": {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "timestamp": "TIMESTAMP",
                "level": "TEXT",
                "source": "TEXT",
                "message": "TEXT",
                "details": "TEXT",
            }
        }

        # ACT: Initialise the DatabaseLogStorageAdapter
        _ = adapters.DatabaseLogStorageAdapter(database_service=mock_database_service)

        # ASSERT: Verify that the database service creates the necessary table for logs
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

    @patch("core.adapters.storage.datetime")
    def test_log_event(self, mock_datetime):
        """Test that the log_event method saves a log entry to the database."""
        # ARRANGE: Create an instance of the DatabaseLogStorageAdapter with a mock database service
        mock_database_service = MagicMock(spec=DatabaseServiceProtocol)
        adapter = adapters.DatabaseLogStorageAdapter(
            database_service=mock_database_service
        )

        mock_datetime.now.return_value.strftime.return_value = "2026-03-12 12:00:00"

        test_cases = [
            {
                "level": "INFO",
                "source": "TestModule",
                "message": "This is a test log message.",
                "details": None,
                "description": "Log message without details",
            },
            {
                "level": "ERROR",
                "source": "TestModule",
                "message": "An error occurred.",
                "details": '{"error_code": 123, "error_message": "Something went wrong."}',
                "description": "Log message with details",
            },
        ]

        for case in test_cases:
            with self.subTest(case["description"]):
                # ACT: Call the log_event method of the adapter
                adapter.log_event(
                    level=case["level"],
                    source=case["source"],
                    message=case["message"],
                    details=case["details"],
                )

                # ASSERT: Verify that the database service's insert method was called with the correct parameters
                # to save the log entry
                mock_database_service.insert.assert_called_with(
                    table="logs",
                    data={
                        "timestamp": "2026-03-12 12:00:00",
                        "level": case["level"],
                        "source": case["source"],
                        "message": case["message"],
                        "details": case["details"],
                    },
                )

    def test_get_recent_logs(self):
        """Test that the get_recent_logs method retrieves recent log entries from the database."""
        # ARRANGE: Create an instance of the DatabaseLogStorageAdapter with a mock database service
        mock_database_service = MagicMock(spec=DatabaseServiceProtocol)
        adapter = adapters.DatabaseLogStorageAdapter(
            database_service=mock_database_service
        )

        mock_logs_list = [
            {
                "id": 2,
                "timestamp": "2026-03-12 12:01:00",
                "level": "ERROR",
                "source": "TestModule",
                "message": "An error occurred.",
                "details": '{"error_code": 123, "error_message": "Something went wrong."}',
            },
            {
                "id": 1,
                "timestamp": "2026-03-12 12:00:00",
                "level": "INFO",
                "source": "TestModule",
                "message": "This is a test log message.",
                "details": None,
            },
        ]

        # Patch the select method to simulate filtering by level and limit
        def select_side_effect(table, headers, conditions=None, limit=None):
            # Simulate filtering by level
            filtered = mock_logs_list
            if conditions and "level" in conditions:
                filtered = [
                    log for log in filtered if log["level"] == conditions["level"]
                ]

            # Simulate limit (None, 0, negative, or positive)
            if limit is not None and limit > 0:
                filtered = filtered[:limit]

            return filtered

        mock_database_service.select.side_effect = select_side_effect

        test_cases = [
            {
                "limit": None,
                "level": None,
                "expected_logs": mock_logs_list,
                "description": "Get recent logs with no limit and no level",
            },
            {
                "limit": 1,
                "level": None,
                "expected_logs": [mock_logs_list[0]],
                "description": "Get recent logs with a limit of 1 and no level",
            },
            {
                "limit": 0,
                "level": None,
                "expected_logs": mock_logs_list,
                "description": "Get recent logs with a limit of 0 (should return all) and no level",
            },
            {
                "limit": 10,
                "level": None,
                "expected_logs": mock_logs_list,
                "description": "Get recent logs with a limit greater than the number of logs (should return all) and no level",
            },
            {
                "limit": -1,
                "level": None,
                "expected_logs": mock_logs_list,
                "description": "Get recent logs with a negative limit (should return all) and no level",
            },
            {
                "limit": None,
                "level": "ERROR",
                "expected_logs": [mock_logs_list[0]],
                "description": "Get recent logs with no limit and a specific level",
            },
            {
                "limit": None,
                "level": "WARNING",
                "expected_logs": [],
                "description": "Get recent logs with no limit and a level that has no logs",
            },
            {
                "limit": None,
                "level": "INFO",
                "expected_logs": [mock_logs_list[1]],
                "description": "Get recent logs with no limit and INFO level",
            },
            {
                "limit": 1,
                "level": "INFO",
                "expected_logs": [mock_logs_list[1]],
                "description": "Get recent logs with a limit of 1 and INFO level",
            },
            {
                "limit": 1,
                "level": "ERROR",
                "expected_logs": [mock_logs_list[0]],
                "description": "Get recent logs with a limit of 1 and ERROR level",
            },
            {
                "limit": 1,
                "level": "WARNING",
                "expected_logs": [],
                "description": "Get recent logs with a limit of 1 and a level that has no logs",
            },
        ]

        for case in test_cases:
            with self.subTest(case["description"]):
                # ACT: Call the get_recent_logs method of the adapter
                logs = adapter.get_recent_logs(limit=case["limit"], level=case["level"])

                # ASSERT: Verify that the database service's select method was called with the correct parameters
                conditions = {}
                if case["level"] is not None:
                    conditions["level"] = case["level"]

                mock_database_service.select.assert_called_with(
                    table="logs",
                    headers=[
                        "id",
                        "timestamp",
                        "level",
                        "source",
                        "message",
                        "details",
                    ],
                    conditions=conditions,
                )

                self.assertEqual(logs, case["expected_logs"])

    def test_delete_logs(self):
        """Test that the delete_logs method deletes log entries from the database based on specified conditions."""
        # ARRANGE: Create an instance of the DatabaseLogStorageAdapter with a mock database service
        mock_database_service = MagicMock(spec=DatabaseServiceProtocol)
        adapter = adapters.DatabaseLogStorageAdapter(
            database_service=mock_database_service
        )

        test_cases = [
            {
                "description": "Delete logs with no specific level or source (delete all logs)",
                "level": None,
                "source": None,
            },
            {
                "description": "Delete logs with a specific level",
                "level": "ERROR",
                "source": None,
            },
            {
                "description": "Delete logs with a specific source",
                "level": None,
                "source": "TestModule",
            },
            {
                "description": "Delete logs with a specific level and source",
                "level": "INFO",
                "source": "TestModule",
            },
        ]

        for case in test_cases:
            with self.subTest(case["description"]):
                # ACT: Call the delete_logs method of the adapter
                adapter.delete_logs(level=case["level"], source=case["source"])

                # ASSERT: Verify that the database service's delete method was called with the correct parameters
                conditions = {}
                if case["level"] is not None:
                    conditions["level"] = case["level"]
                if case["source"] is not None:
                    conditions["source"] = case["source"]

                mock_database_service.delete.assert_called_with(
                    table="logs",
                    conditions=conditions,
                )


if __name__ == "__main__":
    unittest.main()
