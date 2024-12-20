"""
This module contains unit tests for the skills in the ACE digital assistant.

These tests ensure that the skills are functioning correctly and providing
the expected responses based on user input and entities.
"""

import os
import random
import unittest
from datetime import datetime
from unittest.mock import patch

from dotenv import load_dotenv
from newsapi.newsapi_exception import NewsAPIException
from requests import exceptions as requests_exceptions
from weatherapi.rest import ApiException

from ace import disable_logging, skills_dict

load_dotenv()

disable_logging("ERROR", "Prevent logging during test_skills.py")


class TestDummySkill(unittest.TestCase):
    """Test the dummy skill to ensure it returns the expected responses.

    The dummy skill is used for testing purposes and does not perform any
    actions. It is used to test the skill handler and ensure that the
    skills are functioning correctly.
    """

    def setUp(self):
        """Provide the setup for the test case.

        Set up the test case by initialising the dummy skill and setting
        the random seed for reproducibility.
        """
        self.skill = skills_dict["DUMMY_SKILL"]
        random.seed(42)

    def test_dummy_skill_no_entities(self):
        """Test the dummy skill with no entities."""
        self.assertEqual(self.skill(), "This is a dummy skill. It does nothing.")

    def test_dummy_skill_with_entities(self):
        """Test the dummy skill with entities."""
        self.assertEqual(
            self.skill(entities=["TEST"]),
            "This dummy skill has the following entities: ['TEST']",
        )


class TestGreetingSkill(unittest.TestCase):
    """Test the greeting skill to ensure it returns the expected response.

    The greeting skill responds to the user's greeting with a friendly message.
    The tests check that the skill returns the correct responses based on the
    user input and any variations in the greeting message.
    """

    def test_greeting_skill(self):
        """Test the greeting skill to ensure it returns the expected responses."""

        possible_responses = [
            "Hello! How can I help you?",
            "Hi there! What can I do for you?",
            "Hey! What's up?",
        ]
        self.assertIn(skills_dict["GREETING_SKILL"](), possible_responses)


class TestFarewellSkill(unittest.TestCase):
    """Test the farewell skill to ensure it returns the expected response.

    The farewell skill responds to the user's farewell with a friendly message.
    The tests check that the skill returns the correct responses based on the
    user input and any variations in the farewell message.
    """

    def test_farewell_skill(self):
        """Test the farewell skill to ensure it returns the expected responses."""

        possible_responses = ["Goodbye!", "Bye! See you later.", "See you soon!"]
        self.assertIn(skills_dict["FAREWELL_SKILL"](), possible_responses)


class TestWhoAreYouSkill(unittest.TestCase):
    """Test the skills that introduce ACE to ensure they return the expected responses.

    The skill introduces ACE to the user when they ask who ACE is or what ACE does.
    The tests check that the skill returns a friendly introduction to ACE.
    """

    def test_who_are_you_skill(self):
        """Test the skill that introduces ACE to ensure it returns the expected responses."""

        possible_responses = [
            "I'm ACE, your Artificial Consciousness Engine. I'm here to help with things and tell you what's going on. You can ask me to do stuff for you, or just chat with me!"
        ]
        self.assertIn(skills_dict["WHO_ARE_YOU_SKILL"](), possible_responses)


class TestHowAreYouSkill(unittest.TestCase):
    """Test the skills that respond to "how are you?" to ensure they return the expected responses.

    The skill responds to the user asking "how are you?" with a friendly message. The tests check that
    the skill returns a response in a friendly manner, informing the user that ACE is a digital assistant
    and does not have feelings but is ready to help the user with their requests.
    """

    def test_how_are_you_skill(self):
        """Test the skill that responds to "how are you?" to ensure it returns the expected responses."""

        possible_responses = [
            "As an Artificial Consciousness Engine, I don't have feelings, but I'm ready to help you out. What can I do for you today?"
        ]
        self.assertIn(skills_dict["HOW_ARE_YOU_SKILL"](), possible_responses)


class TestGetWeatherSkill(unittest.TestCase):
    """Test the skill that gets the weather to ensure it returns the expected responses.

    The weather skill fetches the current weather or a forecast for a specific location,
    and returns the weather information to the user. The tests check that the skill
    returns the correct responses based on the weather data and any errors that may occur.
    """

    def setUp(self):
        """Provide the setup for the test case.

        Set up the test case by initialising the get weather skill.
        """
        self.skill = skills_dict["GET_WEATHER_SKILL"]

    @patch("ace.skills.get_weather")
    def test_get_current_weather_with_location(self, mock_call_weather_api):
        """Test the skill that gets the current weather for a specific location."""

        # Setup the test by mocking the API response
        mock_api_response = {
            "current": {
                "temp_c": 15.5,
                "condition": {"text": "Partly cloudy"},
                "feelslike_c": 12.3,
                "humidity": 60,
                "wind_kph": 15,
            },
            "location": {"name": "London"},
        }
        mock_call_weather_api.return_value = mock_api_response

        # Test the skill with the location entity
        entities = {"location": "London"}
        expected_response = (
            "The weather in London is currently Partly cloudy. "
            "The temperature is 15.5°C, and it feels like 12.3°C. "
            "The humidity is 60%, and the wind speed is 15 km/h."
        )

        self.assertEqual(self.skill(entities=entities), expected_response)

    @patch("ace.skills.get_weather")
    def test_get_current_weather_no_location(self, mock_call_weather_api):
        """Test the skill that gets the current weather for the default location."""

        # Setup the test by getting the default location from the environment
        # and mocking the API response
        home_location = os.environ.get("ACE_HOME_LOCATION", "London")
        mock_api_response = {
            "current": {
                "temp_c": 15.5,
                "condition": {"text": "Partly cloudy"},
                "feelslike_c": 12.3,
                "humidity": 60,
                "wind_kph": 15,
            },
            "location": {"name": home_location},
        }

        mock_call_weather_api.return_value = mock_api_response

        # Test the skill without the location entity
        entities = {"timeframe": "current"}
        expected_response = (
            f"The weather in {home_location} is currently Partly cloudy. "
            "The temperature is 15.5°C, and it feels like 12.3°C. "
            "The humidity is 60%, and the wind speed is 15 km/h."
        )

        self.assertEqual(self.skill(entities=entities), expected_response)

    @patch("ace.skills.get_weather")
    def test_get_current_weather_with_errors(self, mock_call_weather_api):
        """Test the skill that gets the current weather with API errors."""

        # Setup the test by defining the parameters for the API exceptions
        parameters = [
            (
                ApiException(status=400),
                f"Sorry, the location provided ({os.environ.get('ACE_HOME_LOCATION', 'London')}) is invalid.",
            ),
            (ApiException(status=401), "Sorry, the weather API key is invalid."),
            (
                ApiException(status=403),
                "Sorry, I've reached the usage limit for the weather API. Please try again later.",
            ),
            (
                ApiException(status=404),
                "Sorry, the weather API is not available right now, please try again later.",
            ),
            (
                ApiException("Generic error"),
                "Sorry, there was an error fetching weather information.",
            ),
        ]

        # Test the skill with the different API errors
        entities = {"timeframe": "current"}

        for error, expected_response in parameters:
            with self.subTest(error=error, expected_response=expected_response):
                mock_call_weather_api.side_effect = error
                self.assertEqual(self.skill(entities), expected_response)

    @patch("ace.skills.get_weather")
    def test_get_future_weather_with_location(self, mock_call_weather_api):
        """Test the skill that gets the weather forecast for a specific location."""

        # Setup the test by mocking the API response
        mock_api_response = {
            "forecast": {
                "forecastday": [
                    {
                        "date": "2021-08-01",
                        "day": {
                            "maxtemp_c": 20.5,
                            "mintemp_c": 15.5,
                            "condition": {"text": "Partly cloudy"},
                            "avghumidity": 60,
                            "maxwind_kph": 15,
                        },
                    }
                ]
            },
            "location": {"name": "London"},
        }
        mock_call_weather_api.return_value = mock_api_response

        # Test the skill with the location entity
        entities = {"timeframe": "tomorrow", "location": "London"}
        expected_response = (
            "The weather in London tomorrow is forecast to be Partly cloudy. "
            "With a high of 20.5°C and a low of 15.5°C. "
            "The average humidity will be 60%, and the maximum wind speed will be 15 km/h."
        )

        self.assertEqual(self.skill(entities=entities), expected_response)

    @patch("ace.skills.get_weather")
    def test_get_future_weather_no_location(self, mock_call_weather_api):
        """Test the skill that gets the weather forecast for the default location."""

        # Setup the test by getting the default location from the environment
        home_location = os.environ.get("ACE_HOME_LOCATION", "London")
        mock_api_response = {
            "forecast": {
                "forecastday": [
                    {
                        "date": "2021-08-01",
                        "day": {
                            "maxtemp_c": 20.5,
                            "mintemp_c": 15.5,
                            "condition": {"text": "Partly cloudy"},
                            "avghumidity": 60,
                            "maxwind_kph": 15,
                        },
                    }
                ]
            },
            "location": {"name": home_location},
        }

        mock_call_weather_api.return_value = mock_api_response

        # Test the skill without the location entity
        entities = {"timeframe": "tomorrow"}
        expected_response = (
            f"The weather in {home_location} tomorrow is forecast to be Partly cloudy. "
            "With a high of 20.5°C and a low of 15.5°C. "
            "The average humidity will be 60%, and the maximum wind speed will be 15 km/h."
        )

        self.assertEqual(self.skill(entities), expected_response)

    @patch("ace.skills.get_weather")
    def test_get_future_weather_with_errors(self, mock_call_weather_api):
        """Test the skill that gets the weather forecast with API errors."""

        # Setup the test by defining the parameters for the API exceptions
        parameters = [
            (
                ApiException(status=400),
                f"Sorry, the location provided ({os.environ.get('ACE_HOME_LOCATION', 'London')}) is invalid.",
            ),
            (ApiException(status=401), "Sorry, the weather API key is invalid."),
            (
                ApiException(status=403),
                "Sorry, I've reached the usage limit for the weather API. Please try again later.",
            ),
            (
                ApiException(status=404),
                "Sorry, the weather API is not available right now, please try again later.",
            ),
            (
                ApiException("Generic error"),
                "Sorry, there was an error fetching weather information.",
            ),
        ]

        # Test the skill with the different API errors
        entities = {"timeframe": "tomorrow"}

        for error, expected_response in parameters:
            with self.subTest(error=error, expected_response=expected_response):
                mock_call_weather_api.side_effect = error
                self.assertEqual(self.skill(entities), expected_response)


class TestTellTimeSkill(unittest.TestCase):
    """Test the skill that tells the time to ensure it returns the expected responses.

    The tell time skill provides the current time or the time after a specified duration.
    The tests check that the skill returns the correct responses based on the current time
    and the time units provided by the user, and any errors that may occur.
    """

    def setUp(self):
        """Provide the setup for the test case.

        Set up the test case by initialising the tell time skill and setting the random
        seed for reproducibility.
        """
        self.skill = skills_dict["TELL_TIME_SKILL"]
        random.seed(42)

    @patch("ace.skills.datetime")
    def test_tell_time_now(self, mock_datetime):
        """Test the skill that tells the current time."""

        # Setup the test by mocking the current time
        mock_datetime.now.return_value = datetime(2021, 8, 1, 12, 0, 0)

        # Test the skill with no entities
        possible_responses = [
            "The current time is 12:00 PM",
            "It's 12:00 PM now",
            "The time is 12:00 PM",
            "It is currently 12:00 PM",
        ]

        entities = {}

        self.assertIn(self.skill(entities), possible_responses)

    @patch("ace.skills.datetime")
    def test_tell_time_future(self, mock_datetime):
        """Test the skill that tells the time after a specified duration."""

        # Setup the test by mocking the current time and setting up
        # the parameters for the different time units
        mock_datetime.now.return_value = datetime(2021, 8, 1, 12, 0, 0)
        parameters = [
            (
                {"timevalue": "1", "timeunit": "hour"},
                [
                    "The time will be 13:00 PM in 1 hour",
                    "It will be 13:00 PM in 1 hour",
                    "The time will be 13:00 PM",
                    "It will be 13:00 PM",
                ],
            ),
            (
                {"timevalue": "30", "timeunit": "minute"},
                [
                    "The time will be 12:30 PM in 30 minutes",
                    "It will be 12:30 PM in 30 minutes",
                    "The time will be 12:30 PM",
                    "It will be 12:30 PM",
                ],
            ),
            (
                {"timevalue": "10", "timeunit": "second"},
                [
                    "The time will be 12:00:10 PM in 10 seconds",
                    "It will be 12:00:10 PM in 10 seconds",
                    "The time will be 12:00:10 PM",
                    "It will be 12:00:10 PM",
                ],
            ),
        ]

        # Test the skill with the different time units
        for entities, expected_responses in parameters:
            with self.subTest(entities=entities, expected_responses=expected_responses):
                actual_response = self.skill(entities)
                self.assertTrue(
                    any(expected in actual_response for expected in expected_responses)
                )


class TestTodoSkill(unittest.TestCase):
    """Test the skill that interacts with the to-do list to ensure it returns the expected responses.

    The to-do skill allows users to manage their tasks by adding, viewing, and completing tasks.
    The tests check that the skill returns the correct responses based on the to-do list data
    and any errors that may occur when interacting with the to-do manager.
    """

    def setUp(self):
        """Provide the setup for the test case.

        Set up the test case by initialising the to-do skill and setting the random seed for
        reproducibility.
        """
        self.skill = skills_dict["TODO_SKILL"]
        random.seed(42)

    @patch("ace.skills.get_todos")
    def test_todo_skill_show_list(self, mock_get_todos):
        """Test the skill that shows the to-do list to ensure it returns the expected responses."""

        # Setup the test by mocking the to-do list and defining the parameters
        mock_get_todos.return_value = [
            {"id": 1, "content": "Task 1", "due": None, "labels": []},
            {"id": 2, "content": "Task 2", "due": None, "labels": []},
        ]

        parameters = [
            {"action": "show"},
            {"action": "show me"},
            {"action": "show my"},
            {"action": "what"},
            {"action": "what is"},
            {"action": "what's"},
            {"action": "give"},
        ]

        # Test the skill with the different parameters
        expected_response = "Here are your tasks for today:\n- Task 1\n- Task 2"

        for entities in parameters:
            with self.subTest(entities=entities):
                self.assertEqual(self.skill(entities), expected_response)

    @patch("ace.skills.get_todos")
    def test_todo_skill_empty_list(self, mock_get_todos):
        """Test the skill that shows an empty to-do list to ensure it returns the expected responses."""

        # Setup the test by mocking an empty to-do list and defining the parameters
        mock_get_todos.return_value = []

        parameters = [
            {"action": "show"},
            {"action": "show me"},
            {"action": "show my"},
            {"action": "what"},
            {"action": "what is"},
            {"action": "what's"},
            {"action": "give"},
        ]

        # Test the skill with the different parameters
        possible_responses = [
            "You don't have any tasks due today.",
            "You're all caught up! No tasks due today.",
            "No tasks due today. Time to relax!",
        ]

        for entities in parameters:
            with self.subTest(entities=entities):
                self.assertIn(self.skill(entities), possible_responses)

    @patch("ace.skills.add_todo")
    def test_todo_skill_add_task(self, mock_add_todo):
        """Test the skill that adds a task to the to-do list to ensure it returns the expected responses."""

        # Setup the test by mocking the API response and defining the parameters
        mock_add_todo.return_value = {
            "id": 3,
            "content": "Task 3",
            "due": None,
            "labels": [],
        }

        parameters = [
            {"action": "add", "task": "Task 3"},
            {"action": "add a task", "task": "Task 3"},
            {"action": "add task", "task": "Task 3"},
        ]

        # Test the skill with the different parameters
        expected_response = "Added 'Task 3' to your list."

        for entities in parameters:
            with self.subTest(entities=entities):
                self.assertEqual(self.skill(entities), expected_response)

    def test_todo_skill_invalid_todo_manager(self):
        """Test the skill to ensure it raises an error when the to-do manager is invalid."""

        # Setup the test by defining the parameters and mocking the API responses
        # for the valid to-do managers
        parameters = [
            ({"action": "show"}),
            ({"action": "add", "task": "Task 4"}),
        ]

        mock_todoist_api = patch("ace.skills.TodoistAPI.add_task")
        mock_todoist_api.return_value = {
            "id": 4,
            "content": "Task 4",
            "due": None,
            "labels ": [],
        }

        # Test the skill with the different parameters
        with patch.dict("os.environ", {"ACE_TODO_MANAGER": "invalid"}):
            for entities in parameters:
                with self.subTest(entities=entities):
                    with self.assertRaises(ValueError):
                        self.skill(entities)

    def test_todo_skill_show_list_api_errors(self):
        """Test the skill that shows the to-do list with API errors to ensure it returns the expected responses."""

        # Setup the test by defining the parameters for the different API errors
        parameters = [
            (
                requests_exceptions.ConnectionError(),
                "Sorry, I can't connect to the to-do service. Please check your internet connection.",
            ),
            (
                requests_exceptions.Timeout(),
                "Sorry, the to-do service is taking too long to respond. Please try again later.",
            ),
            (
                requests_exceptions.HTTPError(),
                "Sorry, there was an error fetching your to-do list. Please try again later.",
            ),
            (
                requests_exceptions.RequestException("Testing: Request error"),
                "Sorry, there was an unexpected error with the to-do service:: Testing: Request error",
            ),
        ]

        # Test the skill with the different API errors
        entities = {"action": "show"}

        for error, expected_response in parameters:
            with self.subTest(error=error, expected_response=expected_response):
                with patch("ace.skills.get_todos", side_effect=error):
                    self.assertEqual(self.skill(entities), expected_response)

    def test_todo_skill_add_task_api_errors(self):
        """Test the skill that adds a task with API errors to ensure it returns the expected responses."""

        # Setup the test by defining the parameters for the different API errors
        parameters = [
            (
                requests_exceptions.ConnectionError("Testing: Connection error"),
                "Sorry, I can't connect to the to-do service. Please check your internet connection.",
            ),
            (
                requests_exceptions.Timeout(),
                "Sorry, the to-do service is taking too long to respond. Please try again later.",
            ),
            (
                requests_exceptions.HTTPError(),
                "Sorry, there was an error fetching your to-do list. Please try again later.",
            ),
            (
                requests_exceptions.RequestException("Testing: Request error"),
                "Sorry, there was an unexpected error with the to-do service:: Testing: Request error",
            ),
        ]

        # Test the skill with the different API errors
        entities = {"action": "add", "task": "Task 5"}

        for error, expected_response in parameters:
            with self.subTest(error=error, expected_response=expected_response):
                with patch("ace.skills.add_todo", side_effect=error):
                    self.assertEqual(self.skill(entities), expected_response)


class TestNewsSkill(unittest.TestCase):
    """Test the skill that gets news updates to ensure it returns the expected responses.

    The news skill fetches the latest news articles based on a specific topic or category
    and returns the news updates to the user. The tests check that the skill returns the
    correct responses based on the news data and any errors that may occur.
    """

    def setUp(self):
        """Provide the setup for the test case.

        Set up the test case by initialising the news skill.
        """
        self.skill = skills_dict["NEWS_SKILL"]

    @patch("ace.skills.get_news")
    def test_news_skill(self, mock_get_news):
        """Test the skill that gets news updates to ensure it returns the expected responses."""

        # Setup the test by defining the parameters for the different news articles
        parameters = [
            (
                {"topic": "technology"},
                [
                    {"title": "Tech News 1", "description": "Description 1"},
                ],
                "Here are the latest technology news articles:\n- Tech News 1: Description 1",
            ),
            (
                {},
                [
                    {"title": "Top News 1", "description": "Description 1"},
                ],
                "Here are the latest top news articles:\n- Top News 1: Description 1",
            ),
            (
                {"topic": "technology"},
                [
                    {"title": "Tech News 1", "description": "Description 1"},
                    {"title": "Tech News 2", "description": "Description 2"},
                ],
                "Here are the latest technology news articles:\n- Tech News 1: Description 1\n\n- Tech News 2: Description 2",
            ),
            (
                {},
                [
                    {"title": "Top News 1", "description": "Description 1"},
                    {"title": "Top News 2", "description": "Description 2"},
                ],
                "Here are the latest top news articles:\n- Top News 1: Description 1\n\n- Top News 2: Description 2",
            ),
            (
                {"topic": "sports"},
                [],
                "Sorry, I couldn't find any news articles on 'sports'.",
            ),
            (
                {},
                [],
                "Sorry, I couldn't find any news articles.",
            ),
        ]

        # Test the skill with the different parameters
        for entities, mock_news, expected_response in parameters:
            with self.subTest(entities=entities, expected_response=expected_response):
                mock_get_news.return_value = mock_news
                self.assertEqual(self.skill(entities), expected_response)

    @patch("ace.skills.get_news")
    def test_news_skill_api_errors(self, mock_get_news):
        """Test the skill that gets news updates with API errors to ensure it returns the expected responses."""

        # Setup the test by defining the parameters for the different API errors
        parameters = [
            (
                "apiKeyDisabled",
                "Your API key has been disabled",
                "Apologies, it appears your API key for the news service has been disabled.",
            ),
            (
                "apiKeyExhausted",
                "Your API key has no more requests available.",
                "Apologies, your API key for the news service has reached its usage limit.",
            ),
            (
                "apiKeyInvalid",
                "Your API key hasn't been entered correctly. Double check it and try again.",
                "Apologies, your API key doesn't seem to be in the correct format.",
            ),
            (
                "apiKeyMissing",
                "Your API key is missing from the request.",
                "Apologies, it appears you haven't provided an API key for the news service.",
            ),
            (
                "parameterInvalid",
                "You've included a parameter in your request which is currently not supported.",
                "Apologies, a parameter in your request is not supported.",
            ),
            (
                "parametersMissing",
                "Required parameters are missing from the request and it cannot be completed.",
                "Apologies, there appears to be missing parameters in your request.",
            ),
            (
                "rateLimited",
                "You have been rate limited. Back off for a while before trying the request again.",
                "Apologies, it seems you've been rate limited. Please try again later.",
            ),
            (
                "sourcesTooMany",
                "You have requested too many sources in a single request.",
                "Apologies, you have requested news from too many sources. Please try again with fewer sources.",
            ),
            (
                "sourceDoesNotExist",
                "You have requested a source which does not exist.",
                "Apologies, one of the sources you requested does not exist.",
            ),
            (
                "unexpectedError",
                "This shouldn't happen, and if it does then it's our fault, not yours.",
                "Apologies, it seems there was an unexpected error with the news service. Please try again later.",
            ),
            (
                "UNKNOWN_API_ERROR",
                "Testing for an error not currently handled that may be added in the future.",
                "Apologies, there was an error fetching news.",
            ),
        ]

        # Test the skill with the different API errors
        entities = {"topic": "technology"}

        for code, message, expected_response in parameters:
            with self.subTest(
                code=code,
                message=message,
                expected_response=expected_response,
            ):
                mock_get_news.side_effect = NewsAPIException(
                    {"code": code, "status": "error", "message": message}
                )
                self.assertEqual(self.skill(entities), expected_response)


if __name__ == "__main__":
    unittest.main()
