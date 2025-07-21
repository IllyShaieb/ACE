"""test_database.py: Tests for the database module in the ACE program.

Ensures that the database-related functionality in the ACE program works as
expected, and that the data is retrieved and updated correctly.
"""

import unittest
import os

from core import database as db


class TestDatabase(unittest.TestCase):
    """Tests for the database module."""

    def setUp(self):
        self.mock_database = "test.db"

    def test_create_database(self):
        """Test a new database is created."""
        db.create_database(self.mock_database)
        self.assertTrue(os.path.exists(self.mock_database))

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

    def tearDown(self):
        os.remove(self.mock_database)


if __name__ == "__main__":
    unittest.main()
