"""Ensure that the storage module works as expected."""

from src.storage import ConversationStorageProtocol, SQLiteConversationStorage


class TestSQLiteConversationStorage:
    """Test the SQLiteConversationStorage class."""

    def test_sql_conversation_storage_conforms_to_protocol(self):
        """Test that SQLiteConversationStorage conforms to the ConversationStorageProtocol."""
        assert isinstance(SQLiteConversationStorage(), ConversationStorageProtocol)

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

        # ACT: Call the save_message method with test data
        storage.save_message("session_1", "user", "Hello, world!")

        # ASSERT: Check that the message was saved successfully
        messages = storage.get_session_messages("session_1")
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello, world!"
        assert messages[0]["timestamp"] is not None

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
