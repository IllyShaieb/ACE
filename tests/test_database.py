"""test_database.py: Tests for the database module in the ACE program.

Ensures that the database-related functionality in the ACE program works as
expected, and that the data is retrieved and updated correctly.
"""

import os
import sqlite3
import unittest

from core import database as db


class TestDatabase(unittest.TestCase):
    """Tests for the database module."""

    def setUp(self):
        self.mock_database = "test.db"

    def test_create_database(self):
        """Test a new database is created."""
        db.create_database(self.mock_database)
        self.assertTrue(os.path.exists(self.mock_database))

    def test_create_conversation_id_retrieval_failure(self):
        """Test that an error is raised when there is an issue with retrieving the conversation ID."""
        with self.assertRaises(sqlite3.Error):
            db.start_conversation(self.mock_database)

    def test_start_conversation(self):
        """Test a new conversation is started."""
        db.create_database(self.mock_database)
        conversation_id = db.start_conversation(self.mock_database)
        self.assertEqual(conversation_id, 1)

    def test_add_and_get_message(self):
        """Test a new message is added to a conversation, and tests that the
        message is retrieved correctly."""
        # Create the database and start the conversation
        db.create_database(self.mock_database)
        conversation_id = db.start_conversation(self.mock_database)

        # Add messages to the conversation
        db.add_message(self.mock_database, conversation_id, "user", "Hello!")
        db.add_message(self.mock_database, conversation_id, "ace", "Hi!")

        # Retrieve the messages from the conversation
        messages = db.get_messages(self.mock_database, conversation_id)

        # Check that the length of the returned messages is correct
        self.assertEqual(len(messages), 2)

        # Check that content in all messages is correct
        self.assertTrue(
            all(
                [
                    messages[0][0] == 1,
                    messages[0][1] == 1,
                    messages[0][2] == "user",
                    messages[0][3] == "Hello!",
                ]
            )
        )

        self.assertTrue(
            all(
                [
                    messages[1][0] == 2,
                    messages[1][1] == 1,
                    messages[1][2] == "ace",
                    messages[1][3] == "Hi!",
                ]
            )
        )

    def test_get_conversations(self):
        """Test that conversations are retrieved correctly."""
        # Create the database and start some conversations
        db.create_database(self.mock_database)
        db.start_conversation(self.mock_database)
        db.start_conversation(self.mock_database)

        # Retrieve the conversations from the database
        conversations = db.get_conversations(self.mock_database)

        # Check that the length of the returned conversations is correct
        self.assertEqual(len(conversations), 2)

        # Check that content in all conversations is correct
        self.assertTrue(all([conversations[0][0] == 1, conversations[1][0] == 2]))

    def test_delete_conversation(self):
        """Test that a conversation can be deleted from the database and the
        remaining conversations are re-indexed."""
        db.create_database(self.mock_database)
        conversation_id_1 = db.start_conversation(self.mock_database)
        _ = db.start_conversation(self.mock_database)
        _ = db.start_conversation(self.mock_database)

        # Delete the first conversation
        db.delete_conversation(self.mock_database, conversation_id_1)

        # Check that the remaining conversations are re-indexed
        conversations = db.get_conversations(self.mock_database)
        self.assertEqual(len(conversations), 2)
        self.assertEqual(conversations[0][0], 1)  # Formerly ID 2
        self.assertEqual(conversations[1][0], 2)  # Formerly ID 3

        # Check that a new conversation gets the next sequential ID
        new_id = db.start_conversation(self.mock_database)
        self.assertEqual(new_id, 3)

    def tearDown(self):
        os.remove(self.mock_database)


if __name__ == "__main__":
    unittest.main()
