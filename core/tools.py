""" "core.tools: Defines functional tools that ACE can use."""

import contextlib
import inspect
import io
import os
import random
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pytz

from core.protocols import LocationServiceProtocol, WeatherServiceProtocol, WeatherUnits


def discover_tools(services: Optional[Dict[str, Any]] = None) -> List[Any]:
    """Automatically discover and return a list of tool classes defined in this module.

    Filters for classes that have the required 'execute' method and aren't helpers.

    Args:
        services (Optional[Dict[str, Any]]): A dictionary of available services that tools
            might depend on.

    Returns:
        List[Any]: A list of tool classes that can be used by ACE.
    """

    # Create an empty list to hold the discovered tool instances.
    tools = []
    services = services or {}

    # Iterate over all members of the current module that are classes.
    current_module = sys.modules[__name__]
    for name, obj in inspect.getmembers(current_module, inspect.isclass):
        # Check if the class is a tool based on the following criteria:
        is_tool = {
            # 1. It must have an 'execute' method.
            "has_execute": hasattr(obj, "execute"),
            # 2. Must have "Tool" at the end of its name.
            "name_ends_with_tool": name.endswith("Tool"),
            # 3. Must have all properties: name, description, parameters_schema
            "has_name": hasattr(obj, "name"),
            "has_description": hasattr(obj, "description"),
            "has_parameters_schema": hasattr(obj, "parameters_schema"),
        }

        if all(is_tool.values()):
            try:
                # If the class has an __init__ method that accepts parameters,
                # we can pass services to it.
                signature = inspect.signature(obj)

                init_args = {}
                for param in signature.parameters.values():
                    if param.name in services:
                        init_args[param.name] = services[param.name]

                tool_instance = obj(**init_args)
                tools.append(tool_instance)

            except Exception as e:
                print(f"Error instantiating tool '{name}': {e}")

    # Returns the list of tool instances.
    return tools


class ClockTool:
    """A simple tool that provides the current time when executed."""

    @property
    def name(self) -> str:
        """Return the name of the tool."""
        return "get_date_time"

    @property
    def description(self) -> str:
        """Return a brief description of the tool's functionality."""
        return (
            "Returns current date/time with UTC offset and timezone name. "
            "Omit 'timezone' for local time—never ask the user for it. "
            "For cross-timezone questions, call twice: once without timezone (local) "
            "and once with the target (e.g. 'Asia/Tokyo'), then compare UTC offsets."
        )

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return a schema defining the parameters required by the tool."""
        return {
            "type": "OBJECT",
            "properties": {
                "format": {
                    "type": "STRING",
                    "description": "'time', 'date', or 'both'. Defaults to 'both'.",
                    "enum": ["time", "date", "both"],
                },
                "timezone": {
                    "type": "STRING",
                    "description": "IANA timezone name (e.g. 'Asia/Tokyo'). Omit for local time.",
                },
            },
            "required": [],
        }

    def execute(
        self, format: str = "both", timezone: Optional[str] = None, **kwargs: Any
    ) -> str:
        """Get the current date and time in the specified format.

        Args:
            format (str): Specify what to return: 'time', 'date', or 'both'.
                Defaults to 'both'.
            timezone (Optional[str]): An optional timezone to convert the date and time to,
                specified as a string like 'Asia/Singapore'. If not provided, defaults to either the system's
                local timezone or the value of the 'DEFAULT_TIMEZONE' environment variable.

        Returns:
            str: The current date and time in the specified format, including the UTC offset and timezone name.
        """
        # 1. Resolve Timezone String
        timezone_str = timezone or os.getenv("DEFAULT_TIMEZONE")

        # Determine the current time, applying the specified timezone if provided.
        # If no timezone is specified, fall back to the system's local time.
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(pytz.utc).astimezone(tz)
        else:
            now = datetime.now().astimezone()

        # 2. Define Formats
        format_map = {
            "date": "%Y-%m-%d",
            "time": "%H:%M:%S %z (%Z)",
        }

        formatted = now.strftime(format_map.get(format, "%Y-%m-%dT%H:%M:%S %z (%Z)"))

        # 3. Sometimes the %Z abbreviation is missing it will show a number so need to
        # default to the IANA timezone string.
        search_pattern = r"\([+-]\d+\)"
        if re.search(search_pattern, formatted):
            tzname = now.tzname() or ""
            label = timezone_str if re.match(r"^[+-]\d+$", tzname) else tzname
            formatted = re.sub(search_pattern, f"({label})", formatted)
        return formatted


class CharacterCounterTool:
    """A tool that counts the number of characters in a given input string."""

    @property
    def name(self) -> str:
        """Return the name of the tool."""
        return "count_characters"

    @property
    def description(self) -> str:
        """Return a brief description of the tool's functionality."""
        return "Counts the number of characters in a given input string."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return a schema defining the parameters required by the tool."""
        return {
            "type": "OBJECT",
            "properties": {
                "input_string": {"type": "STRING"},
                "with_spaces": {
                    "type": "BOOLEAN",
                    "description": "Whether to count spaces as characters.",
                },
                "character": {
                    "type": "STRING",
                    "description": "Optional specific character to count (overrides with_spaces).",
                },
            },
            "required": ["input_string", "with_spaces"],
        }

    def execute(
        self,
        input_string: str,
        with_spaces: bool = True,
        character: Optional[str] = None,
    ) -> int:
        """Given an input string, count the number of characters based on the provided parameters.

        Args:
            input_string (str): The string to analyze.
            with_spaces (bool): Whether to count spaces as characters. Defaults to True.
            character (Optional[str]): If provided, counts only this specific character instead of all characters.

        Returns:
            int: The count of characters based on the specified parameters.
        """
        # If a specific character is provided, count only that character.
        if character is not None:
            return input_string.count(character)

        # Otherwise, count all characters, optionally excluding spaces.
        if not with_spaces:
            return len(input_string) - input_string.count(" ")

        return len(input_string)


class CoinFlipTool:
    """A tool that simulates flipping a coin and returns the result."""

    @property
    def name(self) -> str:
        """Return the name of the tool."""
        return "flip_coin"

    @property
    def description(self) -> str:
        """Return a brief description of the tool's functionality."""
        return "Simulates flipping a coin and returns 'Heads' or 'Tails'."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return a schema defining the parameters required by the tool."""
        return {
            "type": "OBJECT",
            "properties": {
                "times": {
                    "type": "INTEGER",
                    "description": "The number of times to flip the coin. Defaults to 1.",
                }
            },
            "required": [],
        }

    def execute(self, times: int = 1, **kwargs: Any) -> List[str]:
        """Simulate flipping a coin a specified number of times and return the results.

        Args:
            times (int): The number of times to flip the coin. Defaults to 1.

        Returns:
            List[str]: A list of results for each coin flip, either 'Heads' or 'Tails'.
        """
        if times < 1:
            return []

        return [random.choice(["Heads", "Tails"]) for _ in range(times)]


class RollDiceTool:
    """A tool that simulates rolling a six-sided die and returns the result."""

    @property
    def name(self) -> str:
        """Return the name of the tool."""
        return "roll_dice"

    @property
    def description(self) -> str:
        """Return a brief description of the tool's functionality."""
        return "Simulates rolling a number of dice with the given number of sides"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return a schema defining the parameters required by the tool."""
        return {
            "type": "OBJECT",
            "properties": {
                "dice": {
                    "type": "ARRAY",
                    "description": "A list of dice to roll, where each die is represented as a string like 'd6' or 'd20'. Defaults to 1d6.",
                    "items": {"type": "STRING", "pattern": "^d\\d+$"},
                }
            },
            "required": [],
        }

    def execute(
        self, dice: Optional[List[str]] = None, **kwargs: Any
    ) -> List[Tuple[str, List[int]]]:
        """Simulate rolling a number of dice with the given number of sides.

        Args:
            dice (Optional[List[str]]): A list of dice to roll, where each die is represented
                as a string like 'd6' or 'd20'. Defaults to 1d6.

        Returns:
            List[Tuple[str, List[int]]]: A list of tuples, where each tuple contains the die
                type and the result of all the rolls.
        """
        # If no dice are specified, default to rolling one six-sided die (1d6).
        dice = dice or ["1d6"]

        # Loop through the list of dice
        results = []
        for die in dice:
            # Parse the die string (e.g., '2d10' means rolling 2 ten-sided dice)
            count_str, sides_str = die.lower().split("d")
            count = int(count_str) if count_str else 1  # Default to 1
            sides = int(sides_str)

            # Roll the specified number of dice and store the results
            dice_results = [random.randint(1, sides) for _ in range(count)]

            results.append((die, dice_results))

        return results


class WeatherTool:
    """A tool that provides the current weather for a specified location."""

    def __init__(
        self,
        weather_service: WeatherServiceProtocol,
        location_service: LocationServiceProtocol,
    ):
        """Initialize the WeatherTool with a weather service.

        Args:
            weather_service (WeatherServiceProtocol): An instance of a weather service that
                can fetch current weather information for a given location.
            location_service (LocationServiceProtocol): An instance of a location service that
                can fetch location information based on the client's IP address.
        """
        self.weather_service = weather_service
        self.location_service = location_service

    @property
    def name(self) -> str:
        """Return the name of the tool."""
        return "get_weather"

    @property
    def description(self) -> str:
        """Return a brief description of the tool's functionality."""
        return "Provides the current, future (daily), or hourly weather for a specified location."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return a schema defining the parameters required by the tool."""
        return {
            "type": "OBJECT",
            "properties": {
                "location": {
                    "type": "STRING",
                    "description": (
                        "The location to get the weather for, formatted as "
                        "'{city name},{state code},{country code}' using ISO 3166 country codes. "
                        "The state code is only required for US locations. "
                        "Examples: 'London,GB', 'New York,NY,US', 'Paris,FR', 'Tokyo'. "
                        "This is optional; if omitted, the tool will automatically determine the location based on the client's IP address."
                    ),
                },
                "units": {
                    "type": "STRING",
                    "description": "The units for the weather data. Can be 'metric', 'imperial' or 'standard'. Defaults to 'metric'.",
                    "enum": ["metric", "imperial", "standard"],
                },
                "forecast_type": {
                    "type": "STRING",
                    "description": "The type of weather forecast to retrieve. Can be 'current' for the current conditions, 'minutely' for the next 1 hour, 'daily' for the next 8 days, or 'hourly' for a hour-by-hour breakdown over the next 48 hours. Defaults to 'current'.",
                    "enum": ["current", "minutely", "daily", "hourly"],
                },
            },
            "required": [],
        }

    def execute(
        self,
        location: Optional[str] = None,
        units: str = "metric",
        forecast_type: str = "current",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get the current or future weather for a specified location.

        Args:
            location (Optional[str]): The location to get the weather for, formatted as
                "{city name},{state code},{country code}" using ISO 3166 country codes.
                The state code is only required for US locations.
                Examples: "London,GB", "New York,NY,US", "Paris,FR".
                If omitted, the tool will automatically determine the location based on the client's IP address.
            units (str): The units for the weather data. Can be 'metric', 'imperial' or
                'standard'. Defaults to 'metric'.
            forecast_type (str): The type of weather forecast to retrieve. Can be 'current',
                'minutely' (next 1 hour), 'daily' (8-day daily summary), or 'hourly' (next 48 hours).
                Defaults to 'current'.

        Returns:
            Dict[str, Any]: A dictionary containing the weather information for the specified location.
        """
        # Map the LLM's string to your Enum
        unit_enum = {
            "metric": WeatherUnits.METRIC,
            "imperial": WeatherUnits.IMPERIAL,
            "standard": WeatherUnits.STANDARD,
        }.get(units.lower(), WeatherUnits.STANDARD)

        # Location is optional, default to environment variable or system's local timezone
        default_location = os.getenv("DEFAULT_LOCATION")

        # If no location is provided, try to determine it from the client's IP address using the location service.
        if not location and not default_location:
            try:
                ipinfo_location = self.location_service.get_location()
                country = ipinfo_location.get("country")
                region = ipinfo_location.get("region")

                match (bool(country), bool(region)):
                    case (True, True):
                        location = f"{region},{country}"
                    case (True, False):
                        location = country
                    case (False, True):
                        location = region

            except Exception as e:
                return {"error": f"Failed to determine location from IP: {e}"}

        location = location or default_location

        if not location:
            return {
                "error": "No location provided and unable to determine location from IP."
            }

        match forecast_type.lower():
            case "minutely":
                weather_data = self.weather_service.get_future_weather(
                    location, unit_enum, forecast_type="minutely"
                )
            case "daily":
                weather_data = self.weather_service.get_future_weather(
                    location, unit_enum, forecast_type="daily"
                )
            case "hourly":
                weather_data = self.weather_service.get_future_weather(
                    location, unit_enum, forecast_type="hourly"
                )
            case _:
                weather_data = self.weather_service.get_current_weather(
                    location, unit_enum
                )

        return {"location": location, "weather": weather_data}


class CodeTool:
    """A tool that executes a provided Python source code and returns the output."""

    @property
    def name(self) -> str:
        """Return the name of the tool."""
        return "execute_code"

    @property
    def description(self) -> str:
        """Return a brief description of the tool's functionality."""
        return "Executes a provided code snippet and returns the output."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return a schema defining the parameters required by the tool."""
        return {
            "type": "OBJECT",
            "properties": {
                "code_string": {
                    "type": "STRING",
                    "description": "The Python source code to run.",
                }
            },
            "required": ["code_string"],
        }

    def execute(self, code_string: str, **kwargs: Any) -> str:
        """Executes Python code and captures everything sent to stdout.

        Args:
            code_string (str): The Python source code to run.

        Returns:
            str: The printed output or error message.
        """
        # Create a buffer to hold the output
        f = io.StringIO()

        # Use a clean dictionary for the execution environment
        exposed_vars = {}

        try:
            # Redirect stdout to our StringIO buffer
            with contextlib.redirect_stdout(f):
                exec(code_string, exposed_vars)

            # Return the captured string
            return f.getvalue()

        except Exception as e:
            # If the code fails, return the error so the LLM knows what went wrong
            return f"Execution Error: {type(e).__name__}: {e}"
