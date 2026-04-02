"""core.services.database: Services for interacting with databases."""

import sqlite3
from typing import Any, Dict, List, Optional

from core.adapters.protocols import LogStorageAdapterProtocol


class SQLiteDatabaseService:
    """Service for managing a SQLite database, providing methods for creating databases and tables,
    as well as performing CRUD operations.
    """

    def __init__(
        self,
        database_path: str,
        log_storage_adapter: Optional[LogStorageAdapterProtocol] = None,
    ) -> None:
        """Initialise the SQLiteDatabaseService with the path to the database file.

        Args:
            database_path (str): The file path to the SQLite database.
            log_storage_adapter (Optional[LogStorageAdapterProtocol]): An optional adapter for logging events related to the database service.
                Defaults to None.
        """
        self.database_path = database_path
        self.log_storage_adapter = log_storage_adapter

    def _log_event(
        self, level: str, source: str, message: str, details: Optional[str] = None
    ) -> None:
        """Log an event to the log storage adapter.

        Args:
            level (str): The severity level of the event (e.g., "INFO", "ERROR").
            source (str): The source of the event (e.g., "model", "tool").
            message (str): A descriptive message about the event.
            details (Optional[str]): Additional details or context about the event.
        """
        if self.log_storage_adapter:
            self.log_storage_adapter.log_event(
                level=level, source=source, message=message, details=details
            )

    def create_table(self, configuration: Dict[str, Any]) -> None:
        """Create a table in the database based on the provided configuration.

        Args:
            configuration (Dict[str, Any]): A dictionary containing the table configuration.
                Expected keys include:
                - "table_name": The name of the table to create.
                - "columns": A dictionary mapping column names to their SQLite data types (e.g., {"id": "INTEGER PRIMARY KEY", "name": "TEXT"}).

        Raises:
            RuntimeError: If there is an error connecting to the database or executing the create table operation.
        """
        connection = None
        try:
            with sqlite3.connect(self.database_path) as connection:
                # Set to output rows as dictionaries for easier access to column values by name
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                columns_def = ", ".join(
                    f"{col_name} {col_type}"
                    for col_name, col_type in configuration["columns"].items()
                )
                create_table_query = f"CREATE TABLE IF NOT EXISTS {configuration['table_name']} ({columns_def})"
                cursor.execute(create_table_query)
                connection.commit()
        except sqlite3.Error as e:
            self._log_event(
                level="ERROR",
                source="database_service",
                message=f"Failed to create table: {configuration.get('table_name')}",
                details=str(e),
            )
            raise RuntimeError(f"Failed to create table: {e}")
        finally:
            if connection is not None:
                connection.close()

    def delete_table(self, table_name: str) -> None:
        """Delete an existing table by name.

        Args:
            table_name (str): The name of the table to delete.

        Raises:
            RuntimeError: If there is an error connecting to the database or executing the delete operation.
        """
        connection = None
        try:
            with sqlite3.connect(self.database_path) as connection:
                cursor = connection.cursor()
                drop_table_query = f"DROP TABLE IF EXISTS {table_name}"
                cursor.execute(drop_table_query)
                connection.commit()
        except sqlite3.Error as e:
            self._log_event(
                level="ERROR",
                source="database_service",
                message=f"Failed to delete table: {table_name}",
                details=str(e),
            )
            raise RuntimeError(f"Failed to delete table: {e}")
        finally:
            if connection is not None:
                connection.close()

    def insert(
        self,
        table: str,
        data: Dict[str, Any],
    ) -> None:
        """Inserts new data into a database

        Args:
            table (str): The name of the table to insert data into.
            data (Dict[str, Any]): A dictionary mapping column names to their corresponding values for the new row.
        """
        connection = None
        try:
            with sqlite3.connect(self.database_path) as connection:
                cursor = connection.cursor()
                columns = ", ".join(data.keys())
                placeholders = ", ".join("?" for _ in data)
                insert_query = (
                    f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                )

                parameters = tuple(data.values())

                cursor.execute(insert_query, parameters)
                connection.commit()
        except sqlite3.Error as e:
            self._log_event(
                level="ERROR",
                source="database_service",
                message=f"Failed to insert data into table: {table}",
                details=str(e),
            )
            raise RuntimeError(f"Failed to insert data: {e}")
        finally:
            if connection is not None:
                connection.close()

    def select(
        self,
        table: str,
        headers: Optional[List[str]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        distinct: bool = False,
    ) -> List:
        """Extracts data from a database

        Args:
            table (str): The name of the table to select data from.
            headers (Optional[List[str]]): An optional list of column names to include in the result. If None, all columns will be included.
            conditions (Optional[Dict[str, Any]]): Optional conditions to specify which rows to select. This can be used to filter results based on certain criteria.
            limit (Optional[int]): An optional limit on the number of rows to return. If None
                there will be no limit on the number of rows returned.
            distinct (bool): Whether to return only distinct rows. Defaults to False.

        Returns:
            List: A list of rows matching the select criteria, where each row is represented as a tuple of column values.

        Raises:
            RuntimeError: If there is an error connecting to the database or executing the select operation.
        """
        connection = None
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.row_factory = sqlite3.Row  # Enable named column access
                cursor = connection.cursor()
                columns = ", ".join(headers) if headers else "*"
                distinct_clause = "DISTINCT " if distinct else ""
                select_query = f"SELECT {distinct_clause}{columns} FROM {table}"

                parameters = ()
                if conditions:
                    where_clause = " AND ".join(
                        f"{col} = ?" for col in conditions.keys()
                    )
                    select_query += f" WHERE {where_clause}"
                    parameters = tuple(conditions.values())

                if limit:
                    select_query += f" LIMIT {limit}"

                cursor.execute(select_query, parameters)
                return cursor.fetchall()
        except sqlite3.Error as e:
            self._log_event(
                level="ERROR",
                source="database_service",
                message=f"Failed to select data from table: {table}",
                details=str(e),
            )
            raise RuntimeError(f"Failed to select data: {e}")
        finally:
            if connection is not None:
                connection.close()

    def update(
        self,
        table: str,
        updates: Dict[str, Any],
        conditions: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Updates data in a database

        Args:
            table (str): The name of the table to update data in.
            updates (Dict[str, Any]): A dictionary mapping column names to their new values for the update operation.
            conditions (Optional[Dict[str, Any]]): Optional conditions to specify which rows to update. This can be used to target specific entries based on certain criteria.

        Raises:
            RuntimeError: If there is an error connecting to the database or executing the update operation.
        """
        connection = None
        try:
            with sqlite3.connect(self.database_path) as connection:
                cursor = connection.cursor()
                set_clause = ", ".join(f"{col} = ?" for col in updates.keys())
                update_query = f"UPDATE {table} SET {set_clause}"

                parameters = tuple(updates.values())
                if conditions:
                    where_clause = " AND ".join(
                        f"{col} = ?" for col in conditions.keys()
                    )
                    update_query += f" WHERE {where_clause}"
                    parameters += tuple(conditions.values())

                cursor.execute(update_query, parameters)
                connection.commit()
        except sqlite3.Error as e:
            self._log_event(
                level="ERROR",
                source="database_service",
                message=f"Failed to update data in table: {table}",
                details=str(e),
            )
            raise RuntimeError(f"Failed to update data: {e}")
        finally:
            if connection is not None:
                connection.close()

    def delete(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> None:
        """Deletes data from a database

        Args:
            table (str): The name of the table to delete data from.
            conditions (Optional[Dict[str, Any]]): Optional conditions to specify which rows to delete. This can be used to target specific entries based on certain criteria. If None, all rows in the table will be deleted.

        Raises:
            RuntimeError: If there is an error connecting to the database or executing the delete operation.
        """
        connection = None
        try:
            with sqlite3.connect(self.database_path) as connection:
                cursor = connection.cursor()
                delete_query = f"DELETE FROM {table}"

                parameters = ()
                if conditions:
                    where_clause = " AND ".join(
                        f"{col} = ?" for col in conditions.keys()
                    )
                    delete_query += f" WHERE {where_clause}"
                    parameters = tuple(conditions.values())

                cursor.execute(delete_query, parameters)
                connection.commit()
        except sqlite3.Error as e:
            self._log_event(
                level="ERROR",
                source="database_service",
                message=f"Failed to delete data from table: {table}",
                details=str(e),
            )
            raise RuntimeError(f"Failed to delete data: {e}")
        finally:
            if connection is not None:
                connection.close()
