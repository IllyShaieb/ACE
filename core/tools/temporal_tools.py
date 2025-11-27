"""core.tools.temporal_tools: This module provides tools for retrieving temporal information
such as time and date.
"""

from datetime import datetime

import pytz

from core.tools import TOOL_HANDLERS, register_tool


@register_tool(
    name="GET_TIME",
    description="Provides the current time in a specified timezone.",
    registry=TOOL_HANDLERS,
)
def get_time(timezone: str = "GMT") -> str:
    """Provide the current time in a human-readable format.

    Args:
        timezone (str): The timezone for which to get the current time.
    """
    template = "The current time is {time}."

    try:
        tz = pytz.timezone(timezone)
        time = datetime.now(tz).strftime("%H:%M")

        return template.format(time=time)
    except pytz.UnknownTimeZoneError:
        return f"The timezone '{timezone}' is not recognized."


@register_tool(
    name="GET_DATE",
    description="Provides the current date in a human-readable format.",
    registry=TOOL_HANDLERS,
)
def get_date() -> str:
    """Provide the current date in a human-readable format."""
    now = datetime.now()
    day = now.day
    suffix = (
        "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    )
    return f"Today's date is {now.strftime('%A')} the {day}{suffix} of {now.strftime('%B %Y')}."
