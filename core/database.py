"""database.py: Contains all the database-related functionality for the ACE
program.

This module contains all the database-related functionality for the ACE
program, including methods to connect to the database, retrieve data, and
update data.
"""

import sqlite3


def create_database(database_name: str) -> None:
    """Create a new database with the given name and add the necessary tables.

    Args:
        database_name (str): The name of the database to create.
    """
    # Connect to the database
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()

        # Create the conversations table if it doesn't exist
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS conversations (
                conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP
            );"""
        )

        # Create the messages table if it doesn't exist
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                sender TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES
                    conversations (conversation_id)
            );"""
        )


def start_conversation(database_name: str) -> int:
    """Start a new conversation and return the conversation ID.

    Args:
        database_name (str): The name of the database to use.

    Returns:
        int: The ID of the new conversation.
    """
    # Connect to the database
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()

        # Insert a new conversation into the conversations table
        cursor.execute("""INSERT INTO conversations DEFAULT VALUES;""")

        # Get the conversation ID of the new conversation
        cursor.execute(
            """SELECT conversation_id FROM conversations
                ORDER BY conversation_id DESC LIMIT 1;"""
        )
        conversation_id = cursor.lastrowid

        return conversation_id


def add_message(
    database_name: str, conversation_id: int, sender: str, content: str
) -> None:
    """Add a new message to the specified conversation.

    Args:
        database_name (str): The name of the database to use.
        conversation_id (int): The ID of the conversation to add the message
                                to.
        sender (str): The sender of the message.
        content (str): The content of the message.
    """
    # Connect to the database
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()

        # Insert the new message into the messages table
        cursor.execute(
            """INSERT INTO messages (conversation_id, sender, content)
                VALUES (?, ?, ?);""",
            (conversation_id, sender, content),
        )


def get_messages(database_name: str, conversation_id: int) -> list:
    """Get all the messages for the specified conversation.

    Args:
        database_name (str): The name of the database to use.
        conversation_id (int): The ID of the conversation to get the messages
                                for.

    Returns:
        list: A list of tuples containing the messages for the conversation.
    """
    # Connect to the database
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()

        # Get all the messages for the specified conversation
        cursor.execute(
            """SELECT * FROM messages
                WHERE conversation_id = ?;""",
            (conversation_id,),
        )
        messages = cursor.fetchall()

        return messages
