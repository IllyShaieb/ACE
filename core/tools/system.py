"""core.tools.system: Defines system-level tools that ACE can use, such as getting the current time
or executing code."""

import io
import os
import re
from datetime import datetime
from typing import Any, Dict, Optional

import pytz


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
            "Omit 'timezone' for local time�never ask the user for it. "
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
