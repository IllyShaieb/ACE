"""core.constants.py: This module contains constants used in the ACE application."""

from typing import Final, List

# ------------------------------------------------------------------------------
# -                             IDENTITY & SYSTEM                              -
# ------------------------------------------------------------------------------

# Unique Identifiers
ACE_ID: Final[str] = "ACE"
"""The unique identifier for the ACE assistant."""

USER_ID: Final[str] = "YOU"
"""The unique identifier for the user."""

# System Commands
EXIT_COMMAND: Final[str] = "exit"
"""The command used to exit the ACE application."""


# ------------------------------------------------------------------------------
# -                                 DATABASE                                   -
# ------------------------------------------------------------------------------

ACE_DATABASE: Final[str] = "data/ace.db"
"""The path and filename of the ACE database file."""

NO_DB_MESSAGE: Final[str] = (
    "[INFO] ACE cannot start without a functional database. Exiting."
)
"""The message displayed when the database cannot be initialised."""

# ------------------------------------------------------------------------------
# -                             APPLICATION MESSAGES                           -
# ------------------------------------------------------------------------------

APP_TITLE: Final[str] = "ACE - Artificial Consciousness Engine"
"""The title to be displayed in the application window."""

# Messages
INITIALISING_MESSAGE: Final[str] = "Initialising ACE"
"""The message displayed when ACE is starting up."""

TERMINATION_MESSAGE: Final[str] = "Terminating ACE"
"""The message displayed when ACE is shutting down."""

WELCOME_MESSAGE: Final[str] = (
    "Hello! I am ACE, your personal assistant. How can I help you today?"
)
"""The welcome message displayed to the user upon starting ACE."""

GOODBYE_MESSAGE: Final[str] = "Goodbye! It was a pleasure assisting you."
"""The goodbye message displayed to the user upon exiting ACE."""

EMPTY_RESPONSE_MESSAGE: Final[str] = "I'm sorry, I don't have a response for that."

# ------------------------------------------------------------------------------
# -                                 TOOLS                                      -
# ------------------------------------------------------------------------------

TOOL_NOT_FOUND_MESSAGE: Final[str] = "The requested tool was not found in the registry."
"""This message is returned when a tool is not found in the tool registry."""

# Weather Tool
WEATHER_API_URL: Final[str] = "https://api.weatherapi.com/v1/current.json"
"""The base URL for the weather API used by the GET_WEATHER tool."""

WEATHER_API_TIMEOUT: Final[int] = 5
"""The timeout duration (in seconds) for requests made to the weather API."""

# Web Search Tool
WEB_CLIENT_USER_AGENTS: Final[List[str]] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]
"""A list of user-agent strings to be used by the web client to mimic real browsers and avoid blocking."""
