"""This module handles the configuration settings for the application."""

import logging
import sys
from pathlib import Path

DEFAULT_LOG_PATH = Path("ace.log")
"""The default path for the log file."""

LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(filename)s | %(funcName)s | %(message)s"
"""The format for log messages."""

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
"""The format for timestamps in log messages."""

MUTED_LOGGERS = ["httpx", "httpcore", "groq", "MARKDOWN"]
"""List of loggers to mute to reduce noise in the logs."""


def setup_logging(
    log_file: Path = DEFAULT_LOG_PATH,
    console_level: int | None = logging.INFO,
    file_level: int | None = logging.DEBUG,
):
    """Sets up logging for the application.

    Args:
        log_file (Path): The path to the log file.
        console_level (int | None): The logging level for the console handler.
        file_level (int | None): The logging level for the file handler.
    """
    # Configure the formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_level or logging.NOTSET)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(file_level or logging.NOTSET)

    logging.basicConfig(
        level=min(console_handler.level, file_handler.level),
        handlers=[console_handler, file_handler],
        force=True,
    )

    # Mute specified loggers to reduce noise in the logs
    for name in MUTED_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)

    # Configure the logging level for the "src" logger
    logging.getLogger("src").setLevel(logging.DEBUG)
