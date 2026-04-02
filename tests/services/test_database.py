"""tests.services.test_database: Ensure that the database service can perform basic operations like creating
tables, inserting data, and querying data."""

import sqlite3
import unittest
from unittest.mock import patch

from core import services


class TestSQLiteDatabaseService(unittest.TestCase):
    """Test the SQLiteDatabaseService's ability to manage a SQLite database and perform CRUD operations."""

    @patch("core.services.database.sqlite3.connect")
    def test_create_table_success(self, mock_connect):
        """Verify that `create_table()` successfully creates a new table."""
        # ARRANGE: Create the service and define a sample configuration for creating a table
        database_service = services.SQLiteDatabaseService(":memory:")
        table_config = {
            "table_name": "test_table",
            "columns": {"id": "INTEGER PRIMARY KEY", "name": "TEXT"},
        }
        mock_cursor = (
            mock_connect.return_value.__enter__.return_value.cursor.return_value
        )

        # ACT: Call the `create_table()` method with the sample configuration
        database_service.create_table(table_config)

        # ASSERT: Verify that `sqlite3.connect()` was called with the correct database name
        mock_connect.assert_called_with(":memory:")
        mock_cursor.execute.assert_called_with(
            "CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)"
        )

    @patch("core.services.database.sqlite3.connect")
    def test_create_table_failure(self, mock_connect):
        """Verify that `create_table()` raises an exception if table creation fails."""
        # ARRANGE: Create the service and mock `sqlite3.connect()` to raise an exception
        database_service = services.SQLiteDatabaseService(":memory:")
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        # ACT & ASSERT: Call the `create_table()` method and expect a RuntimeError
        with self.assertRaises(RuntimeError) as context:
            database_service.create_table(
                {
                    "table_name": "test_table",
                    "columns": {"id": "INTEGER PRIMARY KEY", "name": "TEXT"},
                }
            )

        self.assertIn("Failed to create table", str(context.exception))

    @patch("core.services.database.sqlite3.connect")
    def test_delete_table_success(self, mock_connect):
        """Verify that `delete_table()` successfully deletes an existing table."""
        # ARRANGE: Create the service, table and mock the database connection and cursor
        database_service = services.SQLiteDatabaseService(":memory:")
        table_config = {
            "table_name": "test_table",
            "columns": {"id": "INTEGER PRIMARY KEY", "name": "TEXT"},
        }

        mock_cursor = (
            mock_connect.return_value.__enter__.return_value.cursor.return_value
        )

        # ACT: Call the `delete_table()` method with a sample table name
        database_service.create_table(table_config)
        database_service.delete_table("test_table")

        # ASSERT: Verify that `sqlite3.connect()` was called and the correct SQL command was executed
        mock_connect.assert_called_with(":memory:")
        mock_cursor.execute.assert_called_with("DROP TABLE IF EXISTS test_table")

    @patch("core.services.database.sqlite3.connect")
    def test_delete_table_failure(self, mock_connect):
        """Verify that `delete_table()` raises an exception if table deletion fails."""
        # ARRANGE: Create the service and mock `sqlite3.connect()` to raise an exception
        database_service = services.SQLiteDatabaseService(":memory:")
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        # ACT & ASSERT: Call the `delete_table()` method and expect a RuntimeError
        with self.assertRaises(RuntimeError) as context:
            database_service.delete_table("non_existent_table")

        self.assertIn("Failed to delete table", str(context.exception))

    @patch("core.services.database.sqlite3.connect")
    def test_insert_row_success(self, mock_connect):
        """Verify that `insert()` successfully inserts a new row into the table."""
        # ARRANGE: Create the service, table and mock the database connection and cursor
        database_service = services.SQLiteDatabaseService(":memory:")
        table_config = {
            "table_name": "test_table",
            "columns": {"id": "INTEGER PRIMARY KEY", "name": "TEXT"},
        }
        mock_cursor = (
            mock_connect.return_value.__enter__.return_value.cursor.return_value
        )

        test_cases = [
            {
                "data": {"id": 1, "name": "Alice"},
                "expected_query": "INSERT INTO test_table (id, name) VALUES (?, ?)",
                "expected_params": (1, "Alice"),
                "reason": "Should insert a row with integer ID and text name.",
            }
        ]

        # ACT: Call the `insert()` method with sample data
        database_service.create_table(table_config)

        for case in test_cases:
            with self.subTest(msg=case["reason"]):
                database_service.insert(
                    table="test_table",
                    data=case["data"],
                )

                # ASSERT: Verify that the correct SQL command was executed with the expected parameters
                mock_cursor.execute.assert_called_with(
                    case["expected_query"], case["expected_params"]
                )

    @patch("core.services.database.sqlite3.connect")
    def test_insert_row_failure(self, mock_connect):
        """Verify that `insert()` raises an exception if row insertion fails."""
        # ARRANGE: Create the service and mock `sqlite3.connect()` to raise an exception
        database_service = services.SQLiteDatabaseService(":memory:")
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        # ACT & ASSERT: Call the `insert()` method and expect a RuntimeError
        with self.assertRaises(RuntimeError) as context:
            database_service.insert(
                table="test_table",
                data={"id": 1, "name": "Alice"},
            )

        self.assertIn("Failed to insert data", str(context.exception))

    @patch("core.services.database.sqlite3.connect")
    def test_select_row_success(self, mock_connect):
        """Verify that `select()` successfully retrieves data from the table."""
        # ARRANGE: Create the service, table, insert sample data and mock the database connection and cursor
        database_service = services.SQLiteDatabaseService(":memory:")
        table_config = {
            "table_name": "test_table",
            "columns": {"id": "INTEGER PRIMARY KEY", "name": "TEXT"},
        }
        mock_cursor = (
            mock_connect.return_value.__enter__.return_value.cursor.return_value
        )

        database_service.create_table(table_config)
        mock_data = [
            {"id": idx, "name": name}
            for idx, name in enumerate(["A", "B", "C", "C"], start=1)
        ]
        for row in mock_data:
            database_service.insert(
                table="test_table",
                data=row,
            )

        test_cases = [
            {
                "headers": None,
                "conditions": None,
                "limit": None,
                "distinct": False,
                "expected_query": "SELECT * FROM test_table",
                "expected_params": (),
                "expected_result": [
                    (1, "A"),
                    (2, "B"),
                    (3, "C"),
                    (4, "C"),
                ],
                "reason": "Should select all columns and rows without conditions or limits.",
            },
            {
                "headers": ["name"],
                "conditions": {"id": 2},
                "limit": None,
                "distinct": False,
                "expected_query": "SELECT name FROM test_table WHERE id = ?",
                "expected_params": (2,),
                "expected_result": [("B",)],
                "reason": "Should select only the 'name' column for the row with id=2.",
            },
            {
                "headers": ["id"],
                "conditions": {"name": "C"},
                "limit": 1,
                "distinct": False,
                "expected_query": "SELECT id FROM test_table WHERE name = ? LIMIT 1",
                "expected_params": ("C",),
                "expected_result": [(3,)],
                "reason": "Should select only the 'id' column for the first row with name='C' due to the limit of 1.",
            },
            {
                "headers": ["name"],
                "conditions": None,
                "limit": None,
                "distinct": True,
                "expected_query": "SELECT DISTINCT name FROM test_table",
                "expected_params": (),
                "expected_result": [("A",), ("B",), ("C",)],
                "reason": "Should select distinct names without conditions or limits.",
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["reason"]):
                # Mock the cursor's `fetchall()` method to return the expected result
                mock_cursor.fetchall.return_value = case["expected_result"]

                # ACT: Call the `select()` method with the specified parameters
                result = database_service.select(
                    table="test_table",
                    headers=case["headers"],
                    conditions=case["conditions"],
                    limit=case["limit"],
                    distinct=case["distinct"],
                )

                # ASSERT: Verify that the correct SQL command was executed and the result matches expected
                mock_cursor.execute.assert_called_with(
                    case["expected_query"], case["expected_params"]
                )
                self.assertEqual(result, case["expected_result"])

    @patch("core.services.database.sqlite3.connect")
    def test_select_row_failure(self, mock_connect):
        """Verify that `select()` raises an exception if data retrieval fails."""
        # ARRANGE: Create the service and mock `sqlite3.connect()` to raise an exception
        database_service = services.SQLiteDatabaseService(":memory:")
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        # ACT & ASSERT: Call the `select()` method and expect a RuntimeError
        with self.assertRaises(RuntimeError) as context:
            database_service.select(
                table="test_table",
            )

        self.assertIn("Failed to select data", str(context.exception))

    @patch("core.services.database.sqlite3.connect")
    def test_update_row_success(self, mock_connect):
        """Verify that `update()` successfully updates existing rows in the table."""
        # ARRANGE: Create the service, table, insert sample data and mock the database connection and cursor
        database_service = services.SQLiteDatabaseService(":memory:")
        table_config = {
            "table_name": "test_table",
            "columns": {"id": "INTEGER PRIMARY KEY", "name": "TEXT"},
        }
        mock_cursor = (
            mock_connect.return_value.__enter__.return_value.cursor.return_value
        )

        database_service.create_table(table_config)
        mock_data = [
            {"id": idx, "name": name}
            for idx, name in enumerate(["A", "B", "C", "C"], start=1)
        ]
        for row in mock_data:
            database_service.insert(
                table="test_table",
                data=row,
            )

        test_cases = [
            {
                "updates": {"name": "Z"},
                "conditions": {"id": 1},
                "expected_query": "UPDATE test_table SET name = ? WHERE id = ?",
                "expected_params": ("Z", 1),
                "reason": "Should update the name to 'Z' for the row with id=1.",
            },
            {
                "updates": {"name": "Y"},
                "conditions": {"name": "B"},
                "expected_query": "UPDATE test_table SET name = ? WHERE name = ?",
                "expected_params": ("Y", "B"),
                "reason": "Should update the name to 'Y' for the row with name='B'.",
            },
            {
                "updates": {"name": "X"},
                "conditions": None,
                "expected_query": "UPDATE test_table SET name = ?",
                "expected_params": ("X",),
                "reason": "Should update the name to 'X' for all rows since there are no conditions.",
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["reason"]):
                # ACT: Call the `update()` method with the specified parameters
                database_service.update(
                    table="test_table",
                    updates=case["updates"],
                    conditions=case["conditions"],
                )

                # ASSERT: Verify that the correct SQL command was executed with the expected parameters
                mock_cursor.execute.assert_called_with(
                    case["expected_query"], case["expected_params"]
                )

    @patch("core.services.database.sqlite3.connect")
    def test_update_row_failure(self, mock_connect):
        """Verify that `update()` raises an exception if data update fails."""
        # ARRANGE: Create the service and mock `sqlite3.connect()` to raise an exception
        database_service = services.SQLiteDatabaseService(":memory:")
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        # ACT & ASSERT: Call the `update()` method and expect a RuntimeError
        with self.assertRaises(RuntimeError) as context:
            database_service.update(
                table="test_table",
                updates={"name": "Z"},
                conditions={"id": 1},
            )

        self.assertIn("Failed to update data", str(context.exception))

    @patch("core.services.database.sqlite3.connect")
    def test_delete_row_success(self, mock_connect):
        """Verify that `delete()` successfully deletes rows from the table."""
        # ARRANGE: Create the service, table, insert sample data and mock the database connection and cursor
        database_service = services.SQLiteDatabaseService(":memory:")
        table_config = {
            "database": ":memory:",
            "table_name": "test_table",
            "columns": {"id": "INTEGER PRIMARY KEY", "name": "TEXT"},
        }
        mock_cursor = (
            mock_connect.return_value.__enter__.return_value.cursor.return_value
        )

        database_service.create_table(table_config)
        mock_data = [
            {"id": idx, "name": name}
            for idx, name in enumerate(["A", "B", "C", "C"], start=1)
        ]
        for row in mock_data:
            database_service.insert(
                table="test_table",
                data=row,
            )

        test_cases = [
            {
                "conditions": {"id": 1},
                "expected_query": "DELETE FROM test_table WHERE id = ?",
                "expected_params": (1,),
                "reason": "Should delete the row with id=1.",
            },
            {
                "conditions": {"name": "C"},
                "expected_query": "DELETE FROM test_table WHERE name = ?",
                "expected_params": ("C",),
                "reason": "Should delete all rows with name='C'.",
            },
            {
                "conditions": None,
                "expected_query": "DELETE FROM test_table",
                "expected_params": (),
                "reason": "Should delete all rows since there are no conditions.",
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["reason"]):
                # ACT: Call the `delete()` method with the specified conditions
                database_service.delete(
                    table="test_table",
                    conditions=case["conditions"],
                )

                # ASSERT: Verify that the correct SQL command was executed with the expected parameters
                mock_cursor.execute.assert_called_with(
                    case["expected_query"], case["expected_params"]
                )

    @patch("core.services.database.sqlite3.connect")
    def test_delete_row_failure(self, mock_connect):
        """Verify that `delete()` raises an exception if data deletion fails."""
        # ARRANGE: Create the service and mock `sqlite3.connect()` to raise an exception
        database_service = services.SQLiteDatabaseService(":memory:")
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        # ACT & ASSERT: Call the `delete()` method and expect a RuntimeError
        with self.assertRaises(RuntimeError) as context:
            database_service.delete(
                table="test_table",
                conditions={"id": 1},
            )

        self.assertIn("Failed to delete data", str(context.exception))


if __name__ == "__main__":
    unittest.main()
