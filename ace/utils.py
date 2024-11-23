"""
This module contains utility functions for the ACE digital assistant.

These functions provide common functionalities that are used by multiple skills
or modules within ACE. They include:
- Getting weather data from a weather API
- Interacting with a to-do list service
- Fetching news updates from a news API

These utility functions are designed to be reusable and modular, promoting
code organisation and maintainability.
"""

import logging
import os
import re
from datetime import date, timedelta

import weatherapi
from cachetools import TTLCache, cached
from newsapi import NewsApiClient
from todoist_api_python.api import TodoistAPI

from ace.config import (
    CONSOLE_LOG_FORMATTER,
    FILE_LOG_FORMATTER,
    LOG_LEVEL_MAP,
    LOG_PATH,
)


@cached(cache=TTLCache(maxsize=60, ttl=300))
def get_weather(location: str, future_days: int = 0) -> dict:
    """Gets weather data for a given location.

    This function retrieves weather information from the WeatherAPI for the
    specified location. It can fetch either the current weather or the
    forecast for a future date.

    Note: The results are cached for 5 minutes to reduce API calls.

    Args:
        location: The name of the location (city, zip code, etc.).
        future_days: (optional) The number of days into the future
                     for which to fetch the forecast. Defaults to 0 (current weather).

    Returns:
        A dictionary containing the weather information.
    """
    # Setup the WeatherAPI configuration
    weatherapi_config = weatherapi.Configuration()
    weatherapi_config.api_key["key"] = os.environ.get("ACE_WEATHER_API_KEY")

    weatherapi_instance = weatherapi.APIsApi(weatherapi.ApiClient(weatherapi_config))

    if future_days >= 1:
        forecast_date = date.today() + timedelta(days=future_days)
        return weatherapi_instance.forecast_weather(
            q=location, dt=forecast_date.strftime("%Y-%m-%d"), days=future_days
        )
    else:
        return weatherapi_instance.realtime_weather(q=location)


def get_todos(project: str, task_filter: str = None) -> list[dict[str, str]]:
    """Gets the user's to-do list.

    This function retrieves the user's to-do list from a to-do list service
    (currently only Todoist is supported). It filters the tasks based on
    the provided filter string.

    Args:
        project: The name of the project (if applicable).
        task_filter: (optional) A filter string to apply to the tasks.

    Returns:
        A list of dictionaries, where each dictionary represents a task.
    """
    todo_manager = os.environ.get("ACE_TODO_MANAGER", "todoist").lower()

    if todo_manager == "todoist":
        api = TodoistAPI(os.environ.get("ACE_TODO_MANAGER_API_KEY"))
    else:
        raise ValueError(f"Unknown todo manager: {todo_manager}")

    tasks = []
    for task in api.get_tasks(project=project, filter=task_filter):
        tasks.append(
            {
                "id": task.id,
                # Remove URL markdown links from the content
                "content": re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", task.content),
                "due": task.due.date,
                "labels": task.labels,
            }
        )

    return tasks


def add_todo(content: str, project: str = None) -> dict:
    """Adds a task to the user's to-do list.

    This function adds a new task with the given content to the user's
    to-do list (currently only Todoist is supported).

    Args:
        content: The content of the task to be added.
        project: (optional) The name of the project to add the task to.

    Returns:
        A dictionary representing the added task.
    """
    todo_manager = os.environ.get("ACE_TODO_MANAGER", "todoist").lower()
    if todo_manager == "todoist":
        api = TodoistAPI(os.environ.get("ACE_TODO_MANAGER_API_KEY"))
        return api.add_task(content, project=project)
    else:
        raise ValueError(f"Unknown todo manager: {todo_manager}")


@cached(cache=TTLCache(maxsize=100, ttl=86400))
def get_news(topic: str = None, limit: int = 5) -> list[dict[str, str]]:
    """Gets the latest news on a topic.

    This function retrieves news articles from the News API. It can fetch
    top headlines or articles on a specific topic. The results are cached
    to reduce API calls.

    Note: The results are cached for 24 hours to reduce API calls.

    Args:
        topic: (optional) The topic or category of news to fetch.
        limit: (optional) The maximum number of articles to return.
               Defaults to 5.

    Returns:
        A list of dictionaries, where each dictionary represents a news article.
    """
    # Setup the NewsAPI configuration
    news_api = NewsApiClient(api_key=os.environ.get("ACE_NEWS_API_KEY"))
    possible_categories = [
        "business",
        "entertainment",
        "health",
        "science",
        "sports",
        "technology",
    ]

    # If topic provided is in the possible categories, use it as the category
    if topic:
        news = (
            news_api.get_top_headlines(category=topic, language="en")
            if re.match(
                r"^(" + "|".join(possible_categories) + ")$", topic, re.IGNORECASE
            )
            else news_api.get_everything(q=topic, language="en", sort_by="relevancy")
        )
    else:
        news = news_api.get_top_headlines(language="en")

    # Standardise the news article format
    news_articles = [
        {
            "title": article["title"],
            "description": article["description"],
            "url": article["url"],
        }
        for article in news["articles"]
        # Remove articles with [Removed] title or description
        if all([article["title"] != "[Removed]", article["description"] != "[Removed]"])
    ]

    return news_articles[:limit]


def create_logger(logger_name: str, level: int | str = "DEBUG") -> logging.Logger:
    """Creates and configures a logger object.

    This function creates a new logger object with the specified name and
    logging level. It also configures the logger to write logs to a file
    and display logs on the console.

    Args:
        logger_name: The name of the logger to configure.
        level: The logging level to set for the logger (either integer
                or string). Defaults to "DEBUG".

    Returns:
        The configured logger object.
    """
    logger = logging.getLogger(logger_name)

    # Need to check if provided logger level is a string or an integer and ensure
    # level is correct
    logger_level = (
        level
        if isinstance(level, int)
        else LOG_LEVEL_MAP.get(level.upper(), logging.INFO)
    )

    logger.setLevel(logger_level)

    # Setup the handlers in a dictionary for easier configuration
    handlers = {
        "file": {
            "class": logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8"),
            "formatter": FILE_LOG_FORMATTER,
            "level": logging.INFO,
        },
        "console": {
            "class": logging.StreamHandler(),
            "formatter": CONSOLE_LOG_FORMATTER,
            "level": logging.ERROR,
        },
    }

    for handler in handlers.values():
        handler_instance = handler["class"]
        handler_instance.setFormatter(handler["formatter"])
        handler_instance.setLevel(handler["level"])
        logger.addHandler(handler_instance)

    return logger


def disable_logging(log_level: int | str = "CRITICAL") -> None:
    """Disables logging for the module.

    This function disables logging by setting the logging level to a specified level.
    By default, it sets the level to "CRITICAL" to disable all logging.

    Args:
        log_level: The logging level to set to disable logging. Defaults to "CRITICAL".#
    """
    logging.disable(LOG_LEVEL_MAP.get(log_level.upper(), logging.CRITICAL))
