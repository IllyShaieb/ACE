"""
This module contains the skill functions for the ACE digital assistant.

A skill is a function that performs a specific task or action in response to a
user's request. Skills are designed to be modular and extensible, allowing
developers to add new skills and enhance ACE's capabilities.

Each skill function takes a dictionary of entities as input and returns a
string response based on the user's request. The entities are extracted from

The entities dictionary contains the extracted entities from the user's input,
which can include information such as:

* The action to be performed (e.g., "show", "add", "get")
* The location for weather information (e.g., "London", "Paris")
* The topic for news articles (e.g., "technology", "sports")
* The task to be added to the to-do list (e.g., "buy groceries")
* And more!

The skill functions can access external APIs, services, or databases to
retrieve information, perform actions, or provide responses to the user.

Note: Skill function names typically end with "_skill" for consistency.
"""

import os
import re
from datetime import datetime, timedelta
from random import choice

from dotenv import load_dotenv
from newsapi.newsapi_exception import NewsAPIException
from requests import exceptions as requests_exceptions
from weatherapi.rest import ApiException as WeatherApiException

from ace.utils import add_todo, get_news, get_todos, get_weather

load_dotenv()


def dummy_skill(entities: dict[str] = None) -> str:
    """A dummy skill for testing purposes.

    This skill does nothing except demonstrate how to handle entities.
    If entities are provided, it returns a message including the entities.
    Otherwise, it returns a default message.

    Args:
        entities: (optional) A dictionary of entities with their values.

    Returns:
        A string indicating the skill's action.
    """
    if entities:
        return f"This dummy skill has the following entities: {entities}"
    return "This is a dummy skill. It does nothing."


def greeting_skill(entities: dict[str] = None) -> str:
    """Greets the user with a random message.

    This skill selects a random greeting message from a list of possible
    responses and returns it.

    Args:
        entities: (optional) A dictionary of entities. Not currently used
                  in this skill, but included for consistency.

    Returns:
        A string containing a greeting message.
    """
    responses = [
        "Hello! How can I help you?",
        "Hi there! What can I do for you?",
        "Hey! What's up?",
    ]
    return choice(responses)


def farewell_skill(entities: dict[str] = None) -> str:
    """Bids the user farewell with a random message.

    This skill selects a random farewell message from a list of possible
    responses and returns it.

    Args:
        entities: (optional) A dictionary of entities. Not currently used
                  in this skill, but included for consistency.

    Returns:
        A string containing a farewell message.
    """
    responses = ["Goodbye!", "Bye! See you later.", "See you soon!"]
    return choice(responses)


def who_are_you_skill(entities: dict[str] = None) -> str:
    """Introduce ACE to the user.

    This skill provides a brief introduction to ACE, the Artificial
    Consciousness Engine, and explains its purpose.

    Args:
        entities: (optional) A dictionary of entities. Not currently used
                  in this skill, but included for consistency.

    Returns:
        A string containing the introduction message.
    """
    lines = [
        "I'm ACE, your Artificial Consciousness Engine.",
        "I'm here to help with things and tell you what's going on.",
        "You can ask me to do stuff for you, or just chat with me!",
    ]
    return " ".join(lines)


def how_are_you_skill(entities: dict[str] = None) -> str:
    """Respond to the user's inquiry about ACE's well-being.

    This skill responds to the user's inquiry about how ACE is doing.

    Args:
        entities: (optional) A dictionary of entities. Not currently used
                  in this skill, but included for consistency.

    Returns:
        A string containing a response to the user's inquiry.
    """
    lines = [
        "As an Artificial Consciousness Engine, I don't have feelings,",
        "but I'm ready to help you out. What can I do for you today?",
    ]
    return " ".join(lines)


def get_weather_skill(entities: dict[str] = None) -> str:
    """Get the current or future weather forecast for a location.

    This skill retrieves the current or future weather forecast for a
    specified location. The location and timeframe are extracted from the
    entities to determine the weather forecast.

    The timeframe can be one of the following:
    - current/today: Get today's weather forecast
    - tomorrow: Get tomorrow's weather forecast

    Args:
        entities: A dictionary of entities containing the location and
                  timeframe for which the weather forecast is requested.

    Returns:
        A string containing the weather forecast information,  or an error
        message if the request fails.
    """
    # Unpack the entities from the dictionary
    location = entities.get("location", os.environ.get("ACE_HOME_LOCATION", "London"))
    timeframe = entities.get("timeframe", "current")

    # Map the timeframe to the number of days in the future
    timeframe_mapping = {
        "current": 0,
        "today": 0,
        "tomorrow": 1,
    }
    future_days = timeframe_mapping.get(timeframe, 0)

    # Call the weather API to get the weather data
    try:
        api_response = get_weather(location, future_days=future_days)

        # Extract the relevant weather information from the API response
        if future_days == 0:  # Current weather
            current = api_response["current"]
            actual_location = api_response["location"]["name"]
            temp_c = current["temp_c"]
            condition = current["condition"]["text"]
            feelslike_c = current["feelslike_c"]
            humidity = current["humidity"]
            wind_kph = current["wind_kph"]

            response = (
                f"The weather in {actual_location} is currently {condition}. "
                f"The temperature is {temp_c:.1f}°C, and it feels like {feelslike_c:.1f}°C. "
                f"The humidity is {humidity}%, and the wind speed is {wind_kph} km/h."
            )
        else:  # Future weather
            # Extract the forecast for the next day
            forecast = api_response["forecast"]["forecastday"][0]
            actual_location = api_response["location"]["name"]
            max_temp_c = forecast["day"]["maxtemp_c"]
            min_temp_c = forecast["day"]["mintemp_c"]
            condition = forecast["day"]["condition"]["text"]
            average_humidity = forecast["day"]["avghumidity"]
            max_wind_kph = forecast["day"]["maxwind_kph"]

            response = (
                f"The weather in {actual_location} tomorrow is forecast to be {condition}. "
                f"With a high of {max_temp_c:.1f}°C and a low of {min_temp_c:.1f}°C. "
                f"The average humidity will be {average_humidity}%, "
                f"and the maximum wind speed will be {max_wind_kph} km/h."
            )
        return response

    except WeatherApiException as e:
        if e.status == 400:
            return f"Sorry, the location provided ({location}) is invalid."
        elif e.status == 401:
            return "Sorry, the weather API key is invalid."
        elif e.status == 403:
            return "Sorry, I've reached the usage limit for the weather API. Please try again later."
        elif e.status == 404:
            return "Sorry, the weather API is not available right now, please try again later."
        else:  # Generic error message
            return "Sorry, there was an error fetching weather information."

    except KeyError:
        return "Sorry, there was an error processing the weather data."


def tell_time_skill(entities: dict[str] = None) -> str:
    """Tell the current or future time based on the user's request.

    This skill tells the current time or the time in the future based on the
    user's request. The time value (timevalue) and unit (timeunit) are extracted
    from the entities to determine the future time.

    The time unit can be one of the following:
    - hour(s): Get the time in hours from now
    - minute(s): Get the time in minutes from now
    - second(s): Get the time in seconds from now

    Args:
        entities: A dictionary of entities containing the time value and unit.

    Returns:
        A string containing the current or future time based on the request.
    """
    # Unpack the entities from the dictionary
    time_value = entities.get("timevalue", 0)
    time_unit = entities.get("timeunit", None)

    # Check if the time value is asking for the current time
    if time_value == 0:
        response_templates_current = [
            "The current time is {time}",
            "It's {time} now",
            "The time is {time}",
            "It's currently {time}",
        ]

        current_time = datetime.now().strftime("%H:%M %p")
        return choice(response_templates_current).format(time=current_time)

    # Generate the future time based on the time value and unit
    if time_unit:
        response_templates_future = [
            "The time will be {future_time} in {time_value} {time_unit}",
            "It will be {future_time} in {time_value} {time_unit}",
            "The time will be {future_time}",
            "It will be {future_time}",
        ]

        time_format_config = {
            "hour": "%H:%M %p",
            "minute": "%H:%M %p",
            "second": "%H:%M:%S %p",
        }

        plural = "s" if float(time_value) > 1 else ""

        future_time = datetime.now() + timedelta(**{time_unit + "s": int(time_value)})
        future_time = future_time.strftime(
            time_format_config.get(time_unit, "%H:%M %p")
        )

        return choice(response_templates_future).format(
            future_time=future_time,
            time_value=time_value,
            time_unit=time_unit + plural,
        )


def todo_skill(entities: dict[str] = None) -> str:
    """Perform actions related to a to-do list service (e.g., Todoist).

    This skill allows the user to interact with a to-do list service to view, add,
    and manage tasks. The to-do service and API key are read from the environment
    variables (`ACE_TODO_MANAGER` and `ACE_TODO_MANAGER_API_KEY`).

    It currently supports the following actions:
    - Show tasks due today (where entity is "show")
    - Add a new task to the list (where entity is "add")

    TODO: update the environment variable name for the service as currently it's
    set to `ACE_TODOIST_PROJECT` but it should be `ACE_TODO_MANAGER`

    Args:
        entities: A dictionary of entities containing the action and task.

    Returns:
        A string containing the response to the user's request, or an error
        message if the request fails.
    """
    # Unpack the entities from the dictionary and set default values
    action = entities.get("action", "show")
    project = None
    due = datetime.now().strftime("%Y-%m-%d")

    # Get the tasks filter based on different services
    filter_mapping = {"todoist": {"today": f"today|overdue|{due} & !subtask"}}
    task_filter = filter_mapping.get(
        os.environ.get("ACE_TODOIST_PROJECT", "todoist").lower(), {}
    ).get("today")

    try:
        # Check if the entity is related to showing tasks
        if re.match(r"^(show|what|give)", action):

            todos = get_todos(project, task_filter)

            if len(todos) == 0:
                possible_responses = [
                    "You don't have any tasks due today.",
                    "You're all caught up! No tasks due today.",
                    "No tasks due today. Time to relax!",
                ]
                return choice(possible_responses)

            response_text = "Here are your tasks for today:"
            for todo in todos:
                response_text += f"\n- {todo['content']}"
            return response_text

        # Check if the entity is related to adding a task
        if re.match(r"^add", action):
            # Must have a task to add, either from the entities or user input
            task = entities.get("task", None) or input(
                "ACE: What task would you like to add? "
            )

            if not task.strip():
                return "Sorry, I didn't understand what task you wanted to add."

            if task:

                add_todo_content = f"(Added by ACE) {task}"
                add_todo(add_todo_content, project=project)

                return f"Added '{task}' to your list."

            return "Sorry, I didn't understand what task you wanted to add."

        return "Sorry, I didn't understand that. Please try again."

    except requests_exceptions.ConnectionError:
        return "Sorry, I can't connect to the to-do service. Please check your internet connection."
    except requests_exceptions.Timeout:
        return "Sorry, the to-do service is taking too long to respond. Please try again later."
    except requests_exceptions.HTTPError:
        return "Sorry, there was an error fetching your to-do list. Please try again later."
    except requests_exceptions.RequestException as e:
        return f"Sorry, there was an unexpected error with the to-do service:: {e}"


def news_skill(entities: dict[str] = None) -> str:
    """Get the latest news articles based on the user's request.

    This skill retrieves the latest news articles from a news API based on
    the user's request. It can fetch the top news articles or news on a
    specific topic. The news API key is read from the environment variable
    (`ACE_NEWS_API_KEY`).

    Args:
        entities: A dictionary of entities containing the topic for the news.

    Returns:
        A string containing the latest news articles based on the request.
    """
    # Unpack the entities from the dictionary
    topic = entities.get("topic", None)

    # Call the news API to get the news data
    try:
        news = get_news(topic)

        # Extract the relevant news information from the API response
        if news:
            response_text = f"Here are the latest {topic or 'top'} news articles:\n"
            response_text += "\n\n".join(
                f"- {article['title']}: {article['description']}" for article in news
            )
            return response_text

        return (
            f"Sorry, I couldn't find any news articles on '{topic}'."
            if topic
            else "Sorry, I couldn't find any news articles."
        )

    except NewsAPIException as e:
        error_code_map = {
            "apiKeyDisabled": "Apologies, it appears your API key for the news service has been disabled.",
            "apiKeyExhausted": "Apologies, your API key for the news service has reached its usage limit.",
            "apiKeyInvalid": "Apologies, your API key doesn't seem to be in the correct format.",
            "apiKeyMissing": "Apologies, it appears you haven't provided an API key for the news service.",
            "parameterInvalid": "Apologies, a parameter in your request is not supported.",
            "parametersMissing": "Apologies, there appears to be missing parameters in your request.",
            "rateLimited": "Apologies, it seems you've been rate limited. Please try again later.",
            "sourcesTooMany": "Apologies, you have requested news from too many sources. Please try again with fewer sources.",
            "sourceDoesNotExist": "Apologies, one of the sources you requested does not exist.",
            "unexpectedError": "Apologies, it seems there was an unexpected error with the news service. Please try again later.",
        }

        return error_code_map.get(
            e.get_code(), "Apologies, there was an error fetching news."
        )
