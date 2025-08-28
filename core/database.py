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

        return messages if messages else []


def get_conversations(database_name: str) -> list:
    """Get all conversations from the database, sorted by the most recent
    message.

    Args:
        database_name (str): The name of the database to use.

    Returns:
        list: A list of tuples containing the conversation ID and the timestamp
              of the last message (or start time if no messages exist).
    """
    # Connect to the database
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()

        # Get all conversations, ordered by the most recent message timestamp
        cursor.execute(
            """
            SELECT
                c.conversation_id,
                COALESCE(MAX(m.timestamp), c.start_time) AS last_activity
            FROM
                conversations c
            LEFT JOIN
                messages m ON c.conversation_id = m.conversation_id
            GROUP BY
                c.conversation_id
            ORDER BY
                last_activity DESC;
            """
        )
        conversations = cursor.fetchall()

        return conversations if conversations else []


def delete_conversation(database_name: str, conversation_id: int) -> None:
    """Delete a conversation and re-index subsequent conversations.

    Args:
        database_name (str): The name of the database to use.
        conversation_id (int): The ID of the conversation to delete.
    """
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()
        try:
            # Use a transaction to ensure all operations succeed or fail together
            cursor.execute("BEGIN TRANSACTION;")

            # 1. Delete the target conversation and its messages
            cursor.execute(
                "DELETE FROM messages WHERE conversation_id = ?;", (conversation_id,)
            )
            cursor.execute(
                "DELETE FROM conversations WHERE conversation_id = ?;",
                (conversation_id,),
            )

            # 2. Get all conversations with IDs greater than the deleted one
            cursor.execute(
                "SELECT conversation_id FROM conversations WHERE conversation_id > ? ORDER BY conversation_id ASC;",
                (conversation_id,),
            )
            conversations_to_update = cursor.fetchall()

            # Temporarily disable foreign key constraints to allow re-indexing
            cursor.execute("PRAGMA foreign_keys=OFF;")

            # 3. Re-index the remaining conversations and their messages
            for conv_id_tuple in conversations_to_update:
                old_id = conv_id_tuple[0]
                new_id = old_id - 1
                # Update the conversations table
                cursor.execute(
                    "UPDATE conversations SET conversation_id = ? WHERE conversation_id = ?;",
                    (new_id, old_id),
                )
                # Update the messages table
                cursor.execute(
                    "UPDATE messages SET conversation_id = ? WHERE conversation_id = ?;",
                    (new_id, old_id),
                )

            # 4. Update the sequence counter to the new max ID
            cursor.execute(
                "UPDATE sqlite_sequence SET seq = (SELECT MAX(conversation_id) FROM conversations) WHERE name = 'conversations';"
            )

            # Re-enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON;")

            connection.commit()

        except sqlite3.Error as e:
            connection.rollback()
            print(f"An error occurred during conversation deletion: {e}")
            # Re-enable foreign keys in case of failure
            cursor.execute("PRAGMA foreign_keys=ON;")
