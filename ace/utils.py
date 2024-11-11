import os
import re
from datetime import date, timedelta

import weatherapi
from cachetools import TTLCache, cached
from todoist_api_python.api import TodoistAPI


@cached(cache=TTLCache(maxsize=60, ttl=300))
def get_weather(location: str, future_days: int = 0) -> dict:
    """Get the weather for a location."""
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
    """Get the user's todo list."""
    todo_manager = os.environ.get("ACE_TODO_MANAGER", "todoist").lower()

    if todo_manager == "todoist":
        api = TodoistAPI(os.environ.get("ACE_TODOIST_API_KEY"))
    else:
        raise ValueError(f"Unknown todo manager: {todo_manager}")

    tasks = []
    for task in api.get_tasks(project=project, filter=task_filter):
        tasks.append(
            {
                "id": task.id,
                # Need to remove urls markdown links from the content
                # Want to keep the bit of text that is not a link around the square brackets
                "content": re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", task.content),
                "due": task.due.date,
                "labels": task.labels,
            }
        )

    return tasks


def add_todo(content: str, project: str = None) -> dict:
    """Add a task to the user's todo list."""
    todo_manager = os.environ.get("ACE_TODO_MANAGER", "todoist").lower()
    if todo_manager == "todoist":
        api = TodoistAPI(os.environ.get("ACE_TODOIST_API_KEY"))
        return api.add_task(content, project=project)
    else:
        raise ValueError(f"Unknown todo manager: {todo_manager}")
