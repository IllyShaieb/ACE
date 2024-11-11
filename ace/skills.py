import os
import re
from datetime import datetime, timedelta
from random import choice

from dotenv import load_dotenv
from weatherapi.rest import ApiException as WeatherApiException

from ace.utils import add_todo, get_todos, get_weather

load_dotenv()


def dummy_skill(entities=None) -> str:
    """Dummy skill that does nothing. Used for testing."""
    if entities:
        return f"This dummy skill has the following entities: {entities}"
    return "This is a dummy skill. It does nothing."


def greeting_skill(entities=None) -> str:
    """Greeting the user."""
    responses = [
        "Hello! How can I help you?",
        "Hi there! What can I do for you?",
        "Hey! What's up?",
    ]
    return choice(responses)


def farewell_skill(entities=None) -> str:
    """Say goodbye to the user."""
    responses = ["Goodbye!", "Bye! See you later.", "See you soon!"]
    return choice(responses)


def who_are_you_skill(entities=None) -> str:
    """Explain who ACE is."""
    lines = [
        "I'm ACE, your Artificial Consciousness Engine.",
        "I'm here to help with things and tell you what's going on.",
        "You can ask me to do stuff for you, or just chat with me!",
    ]
    return " ".join(lines)


def how_are_you_skill(entities=None) -> str:
    """Ask ACE how it is doing."""
    lines = [
        "As an Artificial Consciousness Engine, I don't have feelings,",
        "but I'm ready to help you out. What can I do for you today?",
    ]
    return " ".join(lines)


def get_weather_skill(entities=None) -> str:
    """Get the current or future weather."""
    location = entities.get("location", os.environ.get("ACE_HOME_LOCATION", "London"))
    timeframe = entities.get("timeframe", "current")

    timeframe_mapping = {
        "current": 0,
        "today": 0,
        "tomorrow": 1,
    }
    future_days = timeframe_mapping.get(timeframe, 0)

    try:
        api_response = get_weather(location, future_days=future_days)

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


def tell_time_skill(entities=None) -> str:
    """Tell the current time or calculate future time."""
    time_value = entities.get("timevalue", 0)
    time_unit = entities.get("timeunit", None)

    if time_value == 0:
        response_templates_current = [
            "The current time is {time}",
            "It's {time} now",
            "The time is {time}",
            "It's currently {time}",
        ]

        current_time = datetime.now().strftime("%H:%M %p")
        return choice(response_templates_current).format(time=current_time)

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


def todo_skill(entities=None) -> str:
    """Manage the user's to-do list."""
    action = entities.get("action", "show")
    project = None
    due = datetime.now().strftime("%Y-%m-%d")

    filter_mapping = {"todoist": {"today": f"today|overdue|{due} & !subtask"}}

    task_filter = filter_mapping.get(
        os.environ.get("ACE_TODOIST_PROJECT", "todoist").lower(), {}
    ).get("today")

    # Check if the entities is show or what
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

    if re.match(r"^add", action):
        # Get the task from the user
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
