"""tests.test_services: Ensure that services are correctly defined and can be used by tools."""

import sqlite3
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from core import services
from core.protocols import HTTPClientAdapterProtocol, WeatherUnits


class TestOpenWeatherMapService(unittest.TestCase):
    """Test the OpenWeatherMapService's ability to fetch weather information using an HTTP client adapter."""

    def setUp(self):
        """Set up common test components."""
        self.mock_http_client_adapter = MagicMock(spec=HTTPClientAdapterProtocol)
        self.weather_service = services.OpenWeatherMapService(
            self.mock_http_client_adapter, api_key="test_api_key"
        )

    def test_get_current_weather_success(self):
        """Verify that `get_current_weather()` returns a dictionary with weather information."""
        # ARRANGE: Define the expected weather information and mock the HTTP client's response
        mock_client_response = {
            WeatherUnits.METRIC: {
                "current": {
                    "temp": 20,
                    "feels_like": 18,
                    "humidity": 60,
                    "wind_speed": 5.2,
                    "weather": [{"description": "Cloudy"}],
                }
            },
            WeatherUnits.IMPERIAL: {
                "current": {
                    "temp": 68,
                    "feels_like": 64,
                    "humidity": 60,
                    "wind_speed": 11.6,
                    "weather": [{"description": "Cloudy"}],
                }
            },
            WeatherUnits.STANDARD: {
                "current": {
                    "temp": 293.15,
                    "feels_like": 291.15,
                    "humidity": 60,
                    "wind_speed": 5.2,
                    "weather": [{"description": "Cloudy"}],
                }
            },
        }
        test_cases = [
            {  # Metric units test case
                "units": WeatherUnits.METRIC,
                "expected_response": {
                    "temperature": "20°C",
                    "feels_like": "18°C",
                    "condition": "Cloudy",
                    "wind_speed": "5.2 m/s",
                    "humidity": "60%",
                },
                "description": "Should return weather information in metric units.",
            },
            {  # Imperial units test case
                "units": WeatherUnits.IMPERIAL,
                "expected_response": {
                    "temperature": "68°F",
                    "feels_like": "64°F",
                    "condition": "Cloudy",
                    "wind_speed": "11.6 mph",
                    "humidity": "60%",
                },
                "description": "Should return weather information in imperial units.",
            },
            {  # Standard units test case
                "units": WeatherUnits.STANDARD,
                "expected_response": {
                    "temperature": "293.15K",
                    "feels_like": "291.15K",
                    "condition": "Cloudy",
                    "wind_speed": "5.2 m/s",
                    "humidity": "60%",
                },
                "description": "Should return weather information in standard units.",
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["description"]):
                # Mock the HTTP client's response to return the expected weather information
                self.mock_http_client_adapter.get.side_effect = [
                    [{"lat": 51.5073, "lon": -0.1276, "name": "London"}],
                    mock_client_response[case["units"]],
                ]

                # ACT: Call the `get_current_weather()` method with the specified location
                # and units
                result = self.weather_service.get_current_weather(
                    location="London,GB", units=case["units"]
                )

                # ASSERT: Verify that the result matches the expected weather information
                self.assertEqual(result, case["expected_response"])

    def test_get_current_weather_location_not_found(self):
        """Verify the service handles invalid locations gracefully."""
        # ARRANGE: Mock the API returning an empty list for a fake city
        self.mock_http_client_adapter.get.return_value = []

        # ACT & ASSERT: Call the `get_current_weather()` method and expect a RuntimeError
        with self.assertRaises(ValueError):
            self.weather_service.get_current_weather(location="FakeCity,FC")

    def test_get_minutely_weather_success(self):
        """Verify that `get_future_weather()` returns correctly formatted data for the minutely forecast."""
        # ARRANGE: Define the expected response for the minutely forecast, which should always be in mm/h
        # regardless of units
        hour_dt = int(datetime(2026, 3, 5, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        expected_http_response = {
            "forecast": [
                # Use list comprehension to generate 60 entries for the minutely forecast
                f"{datetime.fromtimestamp(hour_dt + i * 60, tz=timezone.utc).strftime('%H:%M UTC')}: {i} mm/h"
                for i in range(60)
            ]
        }
        test_cases = [unit for unit in WeatherUnits]

        for case in test_cases:
            with self.subTest(
                msg=f"{case} units should return mm/h for minutely forecast"
            ):
                # ARRANGE: Mock geo + weather responses
                self.mock_http_client_adapter.get.side_effect = [
                    [{"lat": 51.5073, "lon": -0.1276, "name": "London"}],
                    {  # Always in mm/h for minutely forecast, regardless of units
                        "minutely": [
                            {"dt": hour_dt + i * 60, "precipitation": i}
                            for i in range(60)
                        ]
                    },
                ]

                # ACT: Call the `get_future_weather()` method for the minutely forecast
                result = self.weather_service.get_future_weather(
                    location="London,GB",
                    units=case,
                    forecast_type="minutely",
                )

                # ASSERT: Verify the result matches expected and length is 60 (i.e. 1 hour of minutely data)
                self.assertEqual(result, expected_http_response)
                self.assertEqual(len(result["forecast"]), 60)

    def test_get_hourly_weather_success(self):
        """Verify that `get_future_weather()` returns correctly formatted data for the hourly forecast."""
        # ARRANGE: Define the expected response for the hourly forecast, which should be in the correct units
        hour_dt = int(datetime(2026, 3, 5, 12, 0, 0, tzinfo=timezone.utc).timestamp())

        expected_http_response = {
            WeatherUnits.METRIC: {
                "hourly": [
                    {
                        "dt": hour_dt + i * 3600,
                        "temp": 20 + i,
                        "feels_like": 19 + i,
                        "humidity": 60,
                        "wind_speed": 5.2,
                        "weather": [{"description": "Cloudy"}],
                    }
                    for i in range(24)
                ]
            },
            WeatherUnits.IMPERIAL: {
                "hourly": [
                    {
                        "dt": hour_dt + i * 3600,
                        "temp": round(68 + i * 1.8, 1),
                        "feels_like": round(64 + i * 1.8, 1),
                        "humidity": 60,
                        "wind_speed": 11.6,
                        "weather": [{"description": "Cloudy"}],
                    }
                    for i in range(24)
                ]
            },
            WeatherUnits.STANDARD: {
                "hourly": [
                    {
                        "dt": hour_dt + i * 3600,
                        "temp": 293.15 + i,
                        "feels_like": 291.15 + i,
                        "humidity": 60,
                        "wind_speed": 5.2,
                        "weather": [{"description": "Cloudy"}],
                    }
                    for i in range(24)
                ]
            },
        }
        test_cases = [
            {
                "units": WeatherUnits.METRIC,
                "expected_response": {
                    "forecast": [
                        {
                            datetime.fromtimestamp(
                                hour_dt + i * 3600, tz=timezone.utc
                            ).strftime("%H:%M UTC"): {
                                "temp": f"{20 + i}°C",
                                "feels_like": f"{19 + i}°C",
                                "humidity": "60%",
                                "condition": "Cloudy",
                                "wind_speed": "5.2 m/s",
                            }
                        }
                        for i in range(24)
                    ]
                },
                "reason": "Should return weather in metric units.",
            },
            {
                "units": WeatherUnits.IMPERIAL,
                "expected_response": {
                    "forecast": [
                        {
                            datetime.fromtimestamp(
                                hour_dt + i * 3600, tz=timezone.utc
                            ).strftime("%H:%M UTC"): {
                                "temp": f"{68 + i * 1.8:.1f}°F",
                                "feels_like": f"{64 + i * 1.8:.1f}°F",
                                "humidity": "60%",
                                "condition": "Cloudy",
                                "wind_speed": "11.6 mph",
                            }
                        }
                        for i in range(24)
                    ]
                },
                "reason": "Should return weather in imperial units.",
            },
            {
                "units": WeatherUnits.STANDARD,
                "expected_response": {
                    "forecast": [
                        {
                            datetime.fromtimestamp(
                                hour_dt + i * 3600, tz=timezone.utc
                            ).strftime("%H:%M UTC"): {
                                "temp": f"{293.15 + i}K",
                                "feels_like": f"{291.15 + i}K",
                                "humidity": "60%",
                                "condition": "Cloudy",
                                "wind_speed": "5.2 m/s",
                            }
                        }
                        for i in range(24)
                    ]
                },
                "reason": "Should return weather in standard units.",
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["reason"]):
                # ARRANGE: Mock geo + weather responses
                self.mock_http_client_adapter.get.side_effect = [
                    [{"lat": 51.5073, "lon": -0.1276, "name": "London"}],
                    expected_http_response[case["units"]],
                ]

                # ACT: Call the `get_future_weather()` method for the hourly forecast
                result = self.weather_service.get_future_weather(
                    location="London,GB",
                    units=case["units"],
                    forecast_type="hourly",
                )

                # ASSERT: Verify the result matches expected and length is 24 (i.e. 24 hours of hourly data)
                self.assertEqual(result, case["expected_response"])
                self.assertEqual(len(result["forecast"]), 24)

    def test_get_daily_weather_success(self):
        """Verify that `get_future_weather()` returns correctly formatted data for the daily forecast."""
        # ARRANGE: Define the expected response for the daily forecast, which should be in the correct units
        day_dt = int(datetime(2026, 3, 5, tzinfo=timezone.utc).timestamp())
        expected_http_response = {
            WeatherUnits.METRIC: {
                "daily": [
                    {
                        "dt": day_dt + i * 86400,
                        "temp": {"day": 20 + i},
                        "feels_like": {"day": 19 + i},
                        "humidity": 60,
                        "wind_speed": 5.2,
                        "weather": [{"description": "Cloudy"}],
                    }
                    for i in range(7)
                ]
            },
            WeatherUnits.IMPERIAL: {
                "daily": [
                    {
                        "dt": day_dt + i * 86400,
                        "temp": {"day": round(68 + i * 1.8, 1)},
                        "feels_like": {"day": round(64 + i * 1.8, 1)},
                        "humidity": 60,
                        "wind_speed": 11.6,
                        "weather": [{"description": "Cloudy"}],
                    }
                    for i in range(7)
                ]
            },
            WeatherUnits.STANDARD: {
                "daily": [
                    {
                        "dt": day_dt + i * 86400,
                        "temp": {"day": 293.15 + i},
                        "feels_like": {"day": 291.15 + i},
                        "humidity": 60,
                        "wind_speed": 5.2,
                        "weather": [{"description": "Cloudy"}],
                    }
                    for i in range(7)
                ]
            },
        }
        test_cases = [
            {
                "units": WeatherUnits.METRIC,
                "expected_response": {
                    "forecast": [
                        {
                            datetime.fromtimestamp(
                                day_dt + i * 86400, tz=timezone.utc
                            ).strftime("%Y-%m-%d"): {
                                "temp": f"{20 + i}°C",
                                "feels_like": f"{19 + i}°C",
                                "humidity": "60%",
                                "condition": "Cloudy",
                                "wind_speed": "5.2 m/s",
                            }
                        }
                        for i in range(7)
                    ]
                },
                "reason": "Should return weather in metric units.",
            },
            {
                "units": WeatherUnits.IMPERIAL,
                "expected_response": {
                    "forecast": [
                        {
                            datetime.fromtimestamp(
                                day_dt + i * 86400, tz=timezone.utc
                            ).strftime("%Y-%m-%d"): {
                                "temp": f"{68 + i * 1.8:.1f}°F",
                                "feels_like": f"{64 + i * 1.8:.1f}°F",
                                "humidity": "60%",
                                "condition": "Cloudy",
                                "wind_speed": "11.6 mph",
                            }
                        }
                        for i in range(7)
                    ]
                },
                "reason": "Should return weather in imperial units.",
            },
            {
                "units": WeatherUnits.STANDARD,
                "expected_response": {
                    "forecast": [
                        {
                            datetime.fromtimestamp(
                                day_dt + i * 86400, tz=timezone.utc
                            ).strftime("%Y-%m-%d"): {
                                "temp": f"{293.15 + i}K",
                                "feels_like": f"{291.15 + i}K",
                                "humidity": "60%",
                                "condition": "Cloudy",
                                "wind_speed": "5.2 m/s",
                            }
                        }
                        for i in range(7)
                    ]
                },
                "reason": "Should return weather in standard units.",
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["reason"]):
                # ARRANGE: Mock geo + weather responses
                self.mock_http_client_adapter.get.side_effect = [
                    [{"lat": 51.5073, "lon": -0.1276, "name": "London"}],
                    expected_http_response[case["units"]],
                ]

                # ACT: Call the `get_future_weather()` method for the daily forecast
                result = self.weather_service.get_future_weather(
                    location="London,GB",
                    units=case["units"],
                    forecast_type="daily",
                )

                # ASSERT: Verify the result matches expected and length is 7 (i.e. 7 days of daily data)
                self.assertEqual(result, case["expected_response"])
                self.assertEqual(len(result["forecast"]), 7)

    def test_get_future_weather_location_not_found(self):
        """Verify that `get_future_weather()` raises ValueError for unknown locations."""
        # ARRANGE
        self.mock_http_client_adapter.get.return_value = []

        # ACT & ASSERT
        with self.assertRaises(ValueError):
            self.weather_service.get_future_weather(location="FakeCity,FC")


class TestIPInfoLocationService(unittest.TestCase):
    """Test the IPInfoLocationService's ability to fetch location information based on the client's IP address."""

    def setUp(self):
        """Set up common test components."""
        self.mock_http_client_adapter = MagicMock(spec=HTTPClientAdapterProtocol)
        self.location_service = services.IPInfoLocationService(
            self.mock_http_client_adapter, api_key="test_api_key"
        )

    def test_get_location_success(self):
        """Verify that `get_location()` returns a dictionary with location information."""
        # ARRANGE: Define the expected location information and mock the HTTP client's response
        expected_location_info = {
            "city": "London",
            "region": "England",
            "country": "GB",
            "loc": "51.5073,-0.1276",
        }
        self.mock_http_client_adapter.get.return_value = expected_location_info

        # ACT: Call the `get_location()` method
        result = self.location_service.get_location()

        # ASSERT: Verify that the result matches the expected location information
        self.assertEqual(result, expected_location_info)

    def test_get_location_failure(self):
        """Verify the service handles API failures gracefully."""
        # ARRANGE: Mock the API to raise a RuntimeError
        self.mock_http_client_adapter.get.side_effect = RuntimeError("API failure")

        # ACT & ASSERT: Call the `get_location()` method and expect a RuntimeError
        with self.assertRaises(RuntimeError):
            self.location_service.get_location()


class TestSQLiteDatabaseService(unittest.TestCase):
    """Test the SQLiteDatabaseService's ability to manage a SQLite database and perform CRUD operations."""

    @patch("core.services.sqlite3.connect")
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
            "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)"
        )

    @patch("core.services.sqlite3.connect")
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

    @patch("core.services.sqlite3.connect")
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

    @patch("core.services.sqlite3.connect")
    def test_delete_table_failure(self, mock_connect):
        """Verify that `delete_table()` raises an exception if table deletion fails."""
        # ARRANGE: Create the service and mock `sqlite3.connect()` to raise an exception
        database_service = services.SQLiteDatabaseService(":memory:")
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        # ACT & ASSERT: Call the `delete_table()` method and expect a RuntimeError
        with self.assertRaises(RuntimeError) as context:
            database_service.delete_table("non_existent_table")

        self.assertIn("Failed to delete table", str(context.exception))

    @patch("core.services.sqlite3.connect")
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

    @patch("core.services.sqlite3.connect")
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

    @patch("core.services.sqlite3.connect")
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

    @patch("core.services.sqlite3.connect")
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

    @patch("core.services.sqlite3.connect")
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

    @patch("core.services.sqlite3.connect")
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

    @patch("core.services.sqlite3.connect")
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

    @patch("core.services.sqlite3.connect")
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
