import os
from random import choice

from dotenv import load_dotenv
from weatherapi.rest import ApiException as WeatherApiException

from ace.utils import get_weather

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


def current_weather_skill(entities=None) -> str:
    """Get the current weather."""
    location = entities[0] if entities else None
    if not entities:
        location = os.environ.get("ACE_HOME_LOCATION", "London")

    try:
        api_response = get_weather(location)
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

    try:
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
        return response

    except KeyError:
        return "Sorry, there was an error processing the weather data."
