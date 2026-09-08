"""The storage module provides a simple interface for storing information needed by the application."""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Protocol, runtime_checkable

DEFAULT_DB_PATH: Path = Path.cwd() / "conversations.db"
"""The default path for the SQLite database. Set to the current working directory."""

logger = logging.getLogger(__name__)


@runtime_checkable
class ConversationStorage(Protocol):
    """The conversation storage deals with storing and retrieving conversation sessions
    and messages."""

    def create_session(self, session_id: str) -> None: ...

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: list[dict[str, str]] | None = None,
    ) -> None: ...

    def get_session_messages(self, session_id: str) -> list[dict[str, str]]: ...

    def get_recent_sessions(self, limit: int = 10) -> list[str]: ...

    def delete_session(self, session_id: str) -> None: ...


class SQLiteConversationStorage:
    """A simple SQLite-based conversation storage."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        """Initialise the SQLiteConversationStorage with a database path.

        Args:
            db_path (str | Path): The path to the SQLite database file.
                Defaults to DEFAULT_DB_PATH.
        """
        self.db_path = Path(db_path)
        self._conn = sqlite3.connect(self.db_path)

        # Ensure message cascading and relation rules function properly
        self._conn.execute("PRAGMA foreign_keys = ON")

        self._initialise_database()
        logger.info("conversation_storage_opened database_path=%s", self.db_path)

    def _initialise_database(self) -> None:
        """Initialise the database with the required tables."""
        # Create a cursor to execute SQL commands.
        cursor = self._conn.cursor()

        # The sessions table stores session IDs and their creation timestamps.
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        # The messages table stores messages associated with sessions, including
        # the role of the sender and the content of the message.
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    tool_calls TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)

        # Ensure that the changes are saved to the database.
        self._conn.commit()

    def create_session(self, session_id: str) -> None:
        """Create a new session in the database.

        The table

        Args:
            session_id (str): The unique identifier for the session.
        """

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO sessions (session_id) VALUES (?)",
                (session_id,),
            )
            self._conn.commit()
            logger.debug("session_created session_id=%s", session_id)
        except sqlite3.Error as e:
            logger.error(
                "database_error error_type=%s error_message=%s session_id=%s",
                type(e).__name__,
                str(e),
                session_id,
                exc_info=True,
            )

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: list[dict[str, str]] | None = None,
    ) -> None:
        """Save a message to the database for a given session.

        Args:
            session_id (str): The unique identifier for the session.
            role (str): The role of the message sender (e.g., "user", "assistant").
            content (str): The content of the message.
            tool_calls (list[dict[str, str]] | None): Optional tool call information to include in the message.
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content, tool_calls) VALUES (?, ?, ?, ?)",
                (
                    session_id,
                    role,
                    content,
                    json.dumps(tool_calls) if tool_calls else None,
                ),
            )
            self._conn.commit()
            logger.debug(
                "message_saved session_id=%s role=%s content_length=%d has_tool_calls=%s",
                session_id,
                role,
                len(content),
                bool(tool_calls),
            )
        except sqlite3.Error as e:
            logger.error(
                "database_error error_type=%s error_message=%s session_id=%s",
                type(e).__name__,
                str(e),
                session_id,
                exc_info=True,
            )

    def get_session_messages(self, session_id: str) -> list[dict[str, str]]:
        """Retrieve all messages for a given session from the database.

        Args:
            session_id (str): The unique identifier for the session.

        Returns:
            list[dict[str, str]]: A list of messages for the session, each represented as a
                dictionary with keys "role", "content", and "timestamp".
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute(
                "SELECT role, content, created_at, tool_calls FROM messages WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,),
            )
            rows = cursor.fetchall()
            logger.debug(
                "session_messages_loaded session_id=%s message_count=%d",
                session_id,
                len(rows),
            )
            return [
                {
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "tool_calls": row[3],
                }
                for row in rows
            ]
        except sqlite3.Error as e:
            logger.error(
                "database_error error_type=%s error_message=%s session_id=%s",
                type(e).__name__,
                str(e),
                session_id,
                exc_info=True,
            )
            return []

    def get_recent_sessions(self, limit: int = 10) -> list[str]:
        """Retrieve the most recent session IDs from the database.

        Args:
            limit (int): The maximum number of session IDs to retrieve. Defaults to 10.

        Returns:
            list[str]: A list of the most recent session IDs.
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                SELECT session_id FROM sessions
                ORDER BY created_at DESC
                LIMIT ?
            """,
                (limit,),
            )
            rows = cursor.fetchall()
            logger.debug(
                "recent_sessions_loaded limit=%d session_count=%d", limit, len(rows)
            )
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            logger.error(
                "database_error error_type=%s error_message=%s",
                type(e).__name__,
                str(e),
                exc_info=True,
            )
            return []

    def delete_session(self, session_id: str) -> None:
        """Delete a session and its associated messages from the database.

        Args:
            session_id (str): The unique identifier for the session to delete.
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            self._conn.commit()
            logger.info("session_deleted session_id=%s", session_id)
        except sqlite3.Error as e:
            logger.error(
                "database_error error_type=%s error_message=%s session_id=%s",
                type(e).__name__,
                str(e),
                session_id,
                exc_info=True,
            )


if __name__ == "__main__":
    from pprint import pprint

    def main() -> None:
        """Demonstrate creating sessions, storing messages, and retrieving them."""
        storage = SQLiteConversationStorage(":memory:")
        sample_conversations = {
            "session_1": [
                ("user", "Hello, world!"),
                ("assistant", "Hello! How can I assist you today?"),
            ],
            "session_2": [
                ("user", "Tell me a joke."),
                (
                    "assistant",
                    "Why did the developer go broke? Because they used up all their cache.",
                ),
            ],
            "session_3": [
                ("user", "What is 2 + 2?"),
                ("assistant", "4"),
                ("user", "This is a test message."),
                ("assistant", "This is a test response."),
            ],
        }

        for session_id, messages in sample_conversations.items():
            storage.create_session(session_id)
            for role, content in messages:
                storage.save_message(session_id, role, content)

        print("Recent sessions:")
        pprint(storage.get_recent_sessions(limit=5))

        for session_id in sample_conversations:
            print(f"\nMessages in {session_id}:")
            pprint(storage.get_session_messages(session_id))

    main()
