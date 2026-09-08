"""Ensure that the storage module works as expected."""

import json
import logging
import sqlite3
from unittest.mock import MagicMock, patch

import pytest

from src.storage import ConversationStorage, SQLiteConversationStorage


class TestSQLiteConversationStorage:
    """Test the SQLiteConversationStorage class."""

    def test_sql_conversation_storage_conforms_to_protocol(self):
        """Test that SQLiteConversationStorage conforms to the ConversationStorageProtocol."""
        assert isinstance(SQLiteConversationStorage(), ConversationStorage)

    def test_sql_conversation_storage_create_session(self):
        """Test that SQLiteConversationStorage can create a session."""
        # ARRANGE: Create an instance of SQLiteConversationStorage with an in-memory database
        storage = SQLiteConversationStorage(":memory:")

        # ACT: Call the create_session method with a test session ID
        storage.create_session("session_1")

        # ASSERT: Check that the session was created successfully
        assert storage.get_recent_sessions() == ["session_1"]

    def test_sql_conversation_storage_save_message(self):
        """Test that SQLiteConversationStorage can save a message."""
        # ARRANGE: Create an instance of SQLiteConversationStorage with an in-memory database
        storage = SQLiteConversationStorage(":memory:")
        storage.create_session("session_1")
        tool_calls = [
            {
                "tool_name": "example_tool",
                "input": "example_input",
                "output": "example_output",
            }
        ]

        # ACT: Call the save_message method with test data
        storage.save_message(
            "session_1",
            "user",
            "Hello, world!",
            tool_calls,
        )

        # ASSERT: Check that the message was saved successfully
        messages = storage.get_session_messages("session_1")
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello, world!"
        assert messages[0]["timestamp"] is not None
        assert messages[0]["tool_calls"] == json.dumps(tool_calls)

    def test_sql_conversation_storage_delete_session(self):
        """Test that SQLiteConversationStorage can delete a session."""
        # ARRANGE: Create an instance of SQLiteConversationStorage with an in-memory database
        storage = SQLiteConversationStorage(":memory:")
        storage.create_session("session_1")
        storage.save_message("session_1", "user", "Hello, world!")

        # ACT: Call the delete_session method with the test session ID
        storage.delete_session("session_1")

        # ASSERT: Check that the session and its messages were deleted successfully
        assert storage.get_recent_sessions() == []
        assert storage.get_session_messages("session_1") == []

    def test_storage_logs_info_on_open(self, caplog):
        """Verify opening storage emits an informational lifecycle event."""
        # ACT: Open an in-memory storage instance while capturing informational logs
        with caplog.at_level(logging.INFO, logger="src.storage"):
            SQLiteConversationStorage(":memory:")

        # ASSERT: Verify the storage-opened lifecycle event was logged at INFO level
        assert any(
            record.levelno == logging.INFO
            and "conversation_storage_opened" in record.message
            for record in caplog.records
        )

    def test_storage_logs_debug_on_session_created(self, caplog):
        """Verify creating a session emits debug metadata."""
        # ARRANGE: Create an in-memory storage instance
        storage = SQLiteConversationStorage(":memory:")

        # ACT: Create a session while capturing debug logs
        with caplog.at_level(logging.DEBUG, logger="src.storage"):
            storage.create_session("session_1")

        # ASSERT: Verify the session-created event was logged at DEBUG level
        assert any(
            record.levelno == logging.DEBUG
            and "session_created session_id=session_1" in record.message
            for record in caplog.records
        )

    def test_storage_logs_debug_on_message_saved(self, caplog):
        """Verify saving a message logs metadata but excludes its content."""
        # ARRANGE: Create storage and a message containing private data
        storage = SQLiteConversationStorage(":memory:")
        secret_content = "private@example.com account balance"

        # ACT: Save the message while capturing debug logs
        with caplog.at_level(logging.DEBUG, logger="src.storage"):
            storage.create_session("session_1")
            storage.save_message("session_1", "user", secret_content)

        # ASSERT: Verify safe message metadata was logged without the message content
        message_log = next(
            record for record in caplog.records if "message_saved" in record.message
        )
        assert message_log.levelno == logging.DEBUG
        assert f"content_length={len(secret_content)}" in message_log.message
        assert secret_content not in message_log.message

    def test_storage_logs_debug_on_session_messages_loaded(self, caplog):
        """Verify loading session messages emits debug metadata."""
        # ARRANGE: Create storage containing an empty session
        storage = SQLiteConversationStorage(":memory:")
        storage.create_session("session_1")

        # ACT: Load the session messages while capturing debug logs
        with caplog.at_level(logging.DEBUG, logger="src.storage"):
            storage.get_session_messages("session_1")

        # ASSERT: Verify the message-load event was logged at DEBUG level
        assert any(
            record.levelno == logging.DEBUG
            and "session_messages_loaded session_id=session_1 message_count=0"
            in record.message
            for record in caplog.records
        )

    def test_storage_logs_debug_on_recent_sessions_loaded(self, caplog):
        """Verify loading recent sessions emits debug metadata."""
        # ARRANGE: Create an empty in-memory storage instance
        storage = SQLiteConversationStorage(":memory:")

        # ACT: Load recent sessions while capturing debug logs
        with caplog.at_level(logging.DEBUG, logger="src.storage"):
            storage.get_recent_sessions(limit=5)

        # ASSERT: Verify the recent-sessions event was logged at DEBUG level
        assert any(
            record.levelno == logging.DEBUG
            and "recent_sessions_loaded limit=5 session_count=0" in record.message
            for record in caplog.records
        )

    def test_storage_logs_info_on_session_deleted(self, caplog):
        """Verify deleting a session emits an informational lifecycle event."""
        # ARRANGE: Create storage containing a session to delete
        storage = SQLiteConversationStorage(":memory:")
        storage.create_session("session_1")

        # ACT: Delete the session while capturing informational logs
        with caplog.at_level(logging.INFO, logger="src.storage"):
            storage.delete_session("session_1")

        # ASSERT: Verify the session-deleted event was logged at INFO level
        assert any(
            record.levelno == logging.INFO
            and "session_deleted session_id=session_1" in record.message
            for record in caplog.records
        )

    def test_storage_logs_error_on_create_session_sqlite_exception(self, caplog):
        """Verify that an exception during session creation emits an error log."""
        # ARRANGE: Create an in-memory storage instance, and mock the database connection to raise an exception
        storage = SQLiteConversationStorage(":memory:")

        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = sqlite3.Error("Test exception")
        storage._conn = mock_conn

        # ACT: Attempt to create a session while capturing error logs
        with caplog.at_level(logging.ERROR, logger="src.storage"):
            storage.create_session("session_1")

        # ASSERT: Verify that an error message was logged
        assert any(
            record.levelno == logging.ERROR
            and "database_error" in record.message
            and "error_type=Error" in record.message
            for record in caplog.records
        )

    def test_storage_logs_error_on_save_message_sqlite_exception(self, caplog):
        """Verify that an exception during message saving emits an error log."""
        # ARRANGE: Create an in-memory storage instance, and mock the database connection to raise an exception
        storage = SQLiteConversationStorage(":memory:")
        storage.create_session("session_1")

        # ACT: Attempt to save a message while capturing error logs
        with caplog.at_level(logging.ERROR, logger="src.storage"):
            mock_conn = MagicMock()
            mock_conn.cursor.side_effect = sqlite3.Error("Test exception")
            storage._conn = mock_conn
            storage.save_message("session_1", "user", "Hello")

        # ASSERT: Verify that an error message was logged
        assert any(
            record.levelno == logging.ERROR
            and "database_error" in record.message
            and "error_type=Error" in record.message
            for record in caplog.records
        )

    def test_storage_logs_error_on_get_session_messages_sqlite_exception(self, caplog):
        """Verify that an exception during retrieving session messages emits an error log."""
        # ARRANGE: Create an in-memory storage instance, and mock the database connection to raise an exception
        storage = SQLiteConversationStorage(":memory:")
        storage.create_session("session_1")

        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = sqlite3.Error("Test exception")
        storage._conn = mock_conn

        # ACT: Attempt to get session messages while capturing error logs
        with caplog.at_level(logging.ERROR, logger="src.storage"):
            storage.get_session_messages("session_1")

        # ASSERT: Verify that an error message was logged
        assert any(
            record.levelno == logging.ERROR
            and "database_error" in record.message
            and "error_type=Error" in record.message
            for record in caplog.records
        )

    def test_storage_logs_error_on_get_recent_sessions_sqlite_exception(self, caplog):
        """Verify that an exception during retrieving recent sessions emits an error log."""
        # ARRANGE: Create an in-memory storage instance, and mock the database connection to raise an exception
        storage = SQLiteConversationStorage(":memory:")

        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = sqlite3.Error("Test exception")
        storage._conn = mock_conn

        # ACT: Attempt to get recent sessions while capturing error logs
        with caplog.at_level(logging.ERROR, logger="src.storage"):
            storage.get_recent_sessions()

        # ASSERT: Verify that an error message was logged
        assert any(
            record.levelno == logging.ERROR
            and "database_error" in record.message
            and "error_type=Error" in record.message
            for record in caplog.records
        )

    def test_storage_logs_error_on_delete_session_sqlite_exception(self, caplog):
        """Verify that an exception during deleting a session emits an error log."""
        # ARRANGE: Create an in-memory storage instance, and mock the database connection to raise an exception
        storage = SQLiteConversationStorage(":memory:")
        storage.create_session("session_1")

        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = sqlite3.Error("Test exception")
        storage._conn = mock_conn

        # ACT: Attempt to delete a session while capturing error logs
        with caplog.at_level(logging.ERROR, logger="src.storage"):
            storage.delete_session("session_1")

        # ASSERT: Verify that an error message was logged
        assert any(
            record.levelno == logging.ERROR
            and "database_error" in record.message
            and "error_type=Error" in record.message
            for record in caplog.records
        )
