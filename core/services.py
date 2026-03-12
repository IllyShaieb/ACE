""" "core.services: This module defines services for the tools, creating a layer of
abstraction for different APIs the tools might depend on."""

import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.protocols import HTTPClientAdapterProtocol, WeatherUnits


class OpenWeatherMapService:
    """Service for fetching weather information from the OpenWeatherMap API."""

    def __init__(self, http_client_adapter: HTTPClientAdapterProtocol, api_key: str):
        """Initialize the OpenWeatherMapService with an HTTP client adapter and API key.

        Args:
            http_client_adapter (HTTPClientAdapterProtocol): An adapter for making HTTP requests.
            api_key (str): The API key for accessing the OpenWeatherMap API.
        """
        self.http_client_adapter = http_client_adapter
        self.api_key = api_key
        self.geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.weather_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.unit_symbols = {
            WeatherUnits.METRIC: {"temperature": "°C", "wind_speed": "m/s"},
            WeatherUnits.IMPERIAL: {"temperature": "°F", "wind_speed": "mph"},
            WeatherUnits.STANDARD: {"temperature": "K", "wind_speed": "m/s"},
        }

    def get_current_weather(
        self, location: str, units: WeatherUnits = WeatherUnits.STANDARD
    ) -> Dict[str, str]:
        """Get the current weather for a given location.

        Args:
            location (str): The location to fetch weather information for, formatted as
                "{city name},{state code},{country code}" using ISO 3166 country codes.
                The state code is only required for US locations.
                Examples: "London,GB", "New York,NY,US", "Paris,FR".
            units (WeatherUnits): The unit system to use for the weather information.
                Defaults to WeatherUnits.STANDARD.
        Returns:
            Dict[str, str]: The current weather information for the specified location.
        """
        # 1. Get the unit symbols based on the specified units
        symbols = self.unit_symbols[units or WeatherUnits.STANDARD]

        # 2. Handle the network call to fetch geocoding information for the location
        try:
            lat, lon = self._get_geocoding(location).values()
        except ValueError as e:
            raise ValueError(f"Could not find location: {location}") from e
        except RuntimeError as e:
            raise RuntimeError(f"Geocoding API connection failed: {e}") from e

        # 3. Construct the parameters for the weather API call using the geocoding information
        weather_params = {
            "lat": lat,
            "lon": lon,
            "units": units.value if units else WeatherUnits.STANDARD.value,
            "appid": self.api_key,
            "exclude": self._get_exclude_param("current"),
        }

        # 4. Handle the network call to fetch the current weather information using the constructed
        # parameters
        try:
            weather_response = self.http_client_adapter.get(
                self.weather_url, params=weather_params
            )
        except RuntimeError as e:
            raise RuntimeError(f"Failed to fetch weather data: {e}")

        current_weather = weather_response.get("current", {})
        return {
            "temperature": f"{current_weather.get('temp', 'N/A')}{symbols['temperature']}",
            "feels_like": f"{current_weather.get('feels_like', 'N/A')}{symbols['temperature']}",
            "condition": current_weather.get("weather", [{}])[0].get(
                "description", "N/A"
            ),
            "wind_speed": f"{current_weather.get('wind_speed', 'N/A')} {symbols['wind_speed']}",
            "humidity": f"{current_weather.get('humidity', 'N/A')}%",
        }

    def get_future_weather(
        self,
        location: str,
        units: WeatherUnits = WeatherUnits.STANDARD,
        forecast_type: str = "daily",
    ) -> Dict[str, Any]:
        """Get the future weather for a given location.

        Args:
            location (str): The location to fetch weather information for, formatted as
                "{city name},{state code},{country code}" using ISO 3166 country codes.
                The state code is only required for US locations.
                Examples: "London,GB", "New York,NY,US", "Paris,FR".
            units (WeatherUnits): The unit system to use for the weather information.
                Defaults to WeatherUnits.STANDARD.
            forecast_type (str): The type of future forecast to retrieve. Use 'minutely'
                for minute-by-minute updates, 'daily' for a 5-day summary or 'hourly' for
                a hour-by-hour breakdown over the next 12 hours. Defaults to 'daily'.
        Returns:
            Dict[str, Any]: The future weather information for the specified location.

        Raises:
            ValueError: If the location cannot be found.
            RuntimeError: If there is a problem connecting to the APIs.
        """
        # 1. Get the unit symbols based on the specified units
        symbols = self.unit_symbols[units or WeatherUnits.STANDARD]

        # 2. Handle the network call to fetch geocoding information for the location
        try:
            lat, lon = self._get_geocoding(location).values()
        except ValueError as e:
            raise ValueError(f"Could not find location: {location}") from e
        except RuntimeError as e:
            raise RuntimeError(f"Geocoding API connection failed: {e}") from e

        # 3. Construct the parameters for the weather API call using the geocoding information
        weather_params = {
            "lat": lat,
            "lon": lon,
            "units": units.value if units else WeatherUnits.STANDARD.value,
            "appid": self.api_key,
            "exclude": self._get_exclude_param(forecast_type),
        }

        # 4. Handle the network call to fetch the future weather information using the constructed
        # parameters
        try:
            weather_response = self.http_client_adapter.get(
                self.weather_url, params=weather_params
            )
        except RuntimeError as e:
            raise RuntimeError(f"Failed to fetch weather data: {e}")

        match forecast_type:
            case "minutely":
                response = weather_response.get("minutely", [])

                forecast_data = []
                for entry in response[
                    :60
                ]:  # Limit to 1 hour of minutely data (60 entries)
                    dt = datetime.fromtimestamp(entry["dt"], tz=timezone.utc).strftime(
                        "%H:%M UTC"
                    )
                    precipitation = f"{entry.get('precipitation', 'N/A')} mm/h"
                    forecast_data.append(f"{dt}: {precipitation}")

            case "hourly":
                response = weather_response.get("hourly", [])

                forecast_data = []
                for entry in response[:24]:  # Limit to 24 hours of hourly data
                    dt = datetime.fromtimestamp(entry["dt"], tz=timezone.utc).strftime(
                        "%H:%M UTC"
                    )
                    forecast_data.append(
                        {
                            f"{dt}": {
                                "temp": f"{entry.get('temp', 'N/A')}{symbols['temperature']}",
                                "feels_like": f"{entry.get('feels_like', 'N/A')}{symbols['temperature']}",
                                "humidity": f"{entry.get('humidity', 'N/A')}%",
                                "condition": entry.get("weather", [{}])[0].get(
                                    "description", "N/A"
                                ),
                                "wind_speed": f"{entry.get('wind_speed', 'N/A')} {symbols['wind_speed']}",
                            }
                        }
                    )

            case "daily":
                response = weather_response.get("daily", [])

                forecast_data = []
                for entry in response[:7]:  # Limit to 7 days of daily data
                    dt = datetime.fromtimestamp(entry["dt"], tz=timezone.utc).strftime(
                        "%Y-%m-%d"
                    )
                    forecast_data.append(
                        {
                            f"{dt}": {
                                "temp": f"{entry.get('temp', {}).get('day', 'N/A')}{symbols['temperature']}",
                                "condition": entry.get("weather", [{}])[0].get(
                                    "description", "N/A"
                                ),
                                "wind_speed": f"{entry.get('wind_speed', 'N/A')} {symbols['wind_speed']}",
                                "feels_like": f"{entry.get('feels_like', {}).get('day', 'N/A')}{symbols['temperature']}",
                                "humidity": f"{entry.get('humidity', 'N/A')}%",
                            }
                        }
                    )

            case _:
                forecast_data = []

        return {"forecast": forecast_data}

    def _get_geocoding(self, location: str) -> Dict[str, float]:
        """Helper method to fetch geocoding information for a given location.

        Args:
            location (str): The location to fetch geocoding information for.

        Returns:
            Dict[str, float]: The geocoding information including latitude and longitude.

        Raises:
            ValueError: If the location cannot be found.
        """
        try:
            geo_params = {"q": location, "limit": 1, "appid": self.api_key}
            geo_response = self.http_client_adapter.get(self.geo_url, params=geo_params)
        except RuntimeError as e:
            raise RuntimeError(f"Geocoding API connection failed: {e}")

        if not geo_response:
            raise ValueError(f"Could not find location: {location}")

        return {"lat": geo_response[0]["lat"], "lon": geo_response[0]["lon"]}

    def _get_exclude_param(self, forecast_type: str) -> str:
        """Helper method to determine the 'exclude' parameter for the weather API call based on
        the forecast type.

        Args:
            forecast_type (str): The type of future forecast to retrieve.

        Returns:
            str: The 'exclude' parameter value for the weather API call.
        """
        core_exclude = "current,alerts"
        match forecast_type:
            case "minutely":
                exclude = "hourly,daily"
            case "hourly":
                exclude = "minutely,daily"
            case "daily":
                exclude = "minutely,hourly"
            case _:
                exclude = "minutely,hourly,daily,alerts"

        return f"{core_exclude},{exclude}"


class IPInfoLocationService:
    """Service for fetching location information based on IP address using the ipinfo.io API."""

    def __init__(
        self,
        http_client_adapter: HTTPClientAdapterProtocol,
        api_key: Optional[str] = None,
    ):
        """Initialize the IPInfoLocationService with an HTTP client adapter and API key.

        Args:
            http_client_adapter (HTTPClientAdapterProtocol): An adapter for making HTTP requests.
            api_key (Optional[str]): The API key for accessing the ipinfo.io API.
        """
        self.http_client_adapter = http_client_adapter
        self.api_key = api_key

        url_config = {
            "base": "https://ipinfo.io",
            "endpoints": {
                "free": "/json",
                "lite": "/lite/me?token={api_key}",
            },
        }
        self.url = (
            url_config["base"] + url_config["endpoints"]["lite"].format(api_key=api_key)
            if api_key
            else url_config["base"] + url_config["endpoints"]["free"]
        )

    def get_location(self) -> Dict[str, str]:
        """Get the location information based on the client's IP address.

        Returns:
            Dict[str, str]: The location information including city, region, country, and coordinates.
        """
        try:
            if self.api_key:
                response = self.http_client_adapter.get(
                    self.url, headers={"Authorization": f"Bearer {self.api_key}"}
                )
            else:
                response = self.http_client_adapter.get(self.url)
            return {
                "city": response.get("city"),
                "region": response.get("region"),
                "country": response.get("country"),
                "loc": response.get("loc"),  # Latitude and Longitude
            }
        except RuntimeError as e:
            raise RuntimeError(f"Failed to fetch location data: {e}")


class SQLiteDatabaseService:
    """Service for managing a SQLite database, providing methods for creating databases and tables,
    as well as performing CRUD operations.
    """

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

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
                cursor = connection.cursor()
                columns_def = ", ".join(
                    f"{col_name} {col_type}"
                    for col_name, col_type in configuration["columns"].items()
                )
                create_table_query = (
                    f"CREATE TABLE {configuration['table_name']} ({columns_def})"
                )
                cursor.execute(create_table_query)
                connection.commit()
        except sqlite3.Error as e:
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
            raise RuntimeError(f"Failed to delete data: {e}")
        finally:
            if connection is not None:
                connection.close()
