import os
import random
import unittest
from datetime import datetime
from unittest.mock import patch

from dotenv import load_dotenv
from requests import exceptions as requests_exceptions
from weatherapi.rest import ApiException

from ace import skills_dict

load_dotenv()


class TestSkillDummy(unittest.TestCase):
    def setUp(self):
        self.skill = skills_dict["DUMMY_SKILL"]
        random.seed(42)  # Set random seed for reproducibility

    def test_dummy_skill_no_entities(self):
        self.assertEqual(self.skill(), "This is a dummy skill. It does nothing.")

    def test_dummy_skill_with_entities(self):
        self.assertEqual(
            self.skill(entities=["TEST"]),
            "This dummy skill has the following entities: ['TEST']",
        )

    def test_greeting_skill(self):
        possible_responses = [
            "Hello! How can I help you?",
            "Hi there! What can I do for you?",
            "Hey! What's up?",
        ]
        self.assertIn(skills_dict["GREETING_SKILL"](), possible_responses)

    def test_farewell_skill(self):
        possible_responses = ["Goodbye!", "Bye! See you later.", "See you soon!"]
        self.assertIn(skills_dict["FAREWELL_SKILL"](), possible_responses)

    def test_who_are_you_skill(self):
        possible_responses = [
            "I'm ACE, your Artificial Consciousness Engine. I'm here to help with things and tell you what's going on. You can ask me to do stuff for you, or just chat with me!"
        ]
        self.assertIn(skills_dict["WHO_ARE_YOU_SKILL"](), possible_responses)

    def test_how_are_you_skill(self):
        possible_responses = [
            "As an Artificial Consciousness Engine, I don't have feelings, but I'm ready to help you out. What can I do for you today?"
        ]
        self.assertIn(skills_dict["HOW_ARE_YOU_SKILL"](), possible_responses)


class TestSkillGetWeather(unittest.TestCase):
    def setUp(self):
        self.skill = skills_dict["GET_WEATHER_SKILL"]

    @patch("ace.skills.get_weather")
    def test_get_current_weather_with_location(self, mock_call_weather_api):
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
        entities = {"location": "London"}
        expected_response = (
            "The weather in London is currently Partly cloudy. "
            "The temperature is 15.5°C, and it feels like 12.3°C. "
            "The humidity is 60%, and the wind speed is 15 km/h."
        )

        self.assertEqual(self.skill(entities=entities), expected_response)

    @patch("ace.skills.get_weather")
    def test_get_current_weather_no_location(self, mock_call_weather_api):
        # The default location is set in the .env file
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
        entities = {"timeframe": "current"}
        expected_response = (
            f"The weather in {home_location} is currently Partly cloudy. "
            "The temperature is 15.5°C, and it feels like 12.3°C. "
            "The humidity is 60%, and the wind speed is 15 km/h."
        )

        self.assertEqual(self.skill(entities=entities), expected_response)

    @patch("ace.skills.get_weather")
    def test_get_current_weather_with_errors(self, mock_call_weather_api):
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

        entities = {"timeframe": "current"}

        for error, expected_response in parameters:
            with self.subTest(error=error, expected_response=expected_response):
                mock_call_weather_api.side_effect = error
                self.assertEqual(self.skill(entities), expected_response)

    @patch("ace.skills.get_weather")
    def test_get_future_weather_with_location(self, mock_call_weather_api):
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
        entities = {"timeframe": "tomorrow", "location": "London"}

        expected_response = (
            "The weather in London tomorrow is forecast to be Partly cloudy. "
            "With a high of 20.5°C and a low of 15.5°C. "
            "The average humidity will be 60%, and the maximum wind speed will be 15 km/h."
        )

        self.assertEqual(self.skill(entities=entities), expected_response)

    @patch("ace.skills.get_weather")
    def test_get_future_weather_no_location(self, mock_call_weather_api):
        # The default location is set in the .env file
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
        entities = {"timeframe": "tomorrow"}
        expected_response = (
            f"The weather in {home_location} tomorrow is forecast to be Partly cloudy. "
            "With a high of 20.5°C and a low of 15.5°C. "
            "The average humidity will be 60%, and the maximum wind speed will be 15 km/h."
        )

        self.assertEqual(self.skill(entities), expected_response)

    @patch("ace.skills.get_weather")
    def test_get_future_weather_with_errors(self, mock_call_weather_api):
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

        entities = {"timeframe": "tomorrow"}

        for error, expected_response in parameters:
            with self.subTest(error=error, expected_response=expected_response):
                mock_call_weather_api.side_effect = error
                self.assertEqual(self.skill(entities), expected_response)


class TestSkillTellTime(unittest.TestCase):
    def setUp(self):
        self.skill = skills_dict["TELL_TIME_SKILL"]
        random.seed(42)

    @patch("ace.skills.datetime")
    def test_tell_time_now(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2021, 8, 1, 12, 0, 0)

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

        for entities, expected_responses in parameters:
            with self.subTest(entities=entities, expected_responses=expected_responses):
                actual_response = self.skill(entities)
                self.assertTrue(
                    any(expected in actual_response for expected in expected_responses)
                )


class TestSkillTodo(unittest.TestCase):
    def setUp(self):
        self.skill = skills_dict["TODO_SKILL"]
        random.seed(42)

    @patch("ace.skills.get_todos")
    def test_todo_skill_show_list(self, mock_get_todos):
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

        expected_response = "Here are your tasks for today:\n- Task 1\n- Task 2"

        for entities in parameters:
            with self.subTest(entities=entities):
                self.assertEqual(self.skill(entities), expected_response)

    @patch("ace.skills.get_todos")
    def test_todo_skill_empty_list(self, mock_get_todos):
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

        expected_response = "Added 'Task 3' to your list."

        for entities in parameters:
            with self.subTest(entities=entities):
                self.assertEqual(self.skill(entities), expected_response)

    def test_todo_skill_invalid_todo_manager(self):
        parameters = [
            ({"action": "show"}),
            ({"action": "add", "task": "Task 4"}),
        ]

        # Need to mock any installed todo apis
        mock_todoist_api = patch("ace.skills.TodoistAPI.add_task")
        mock_todoist_api.return_value = {
            "id": 4,
            "content": "Task 4",
            "due": None,
            "labels ": [],
        }

        # Mock the environment variable to an invalid value
        with patch.dict("os.environ", {"ACE_TODO_MANAGER": "invalid"}):
            for entities in parameters:
                with self.subTest(entities=entities):
                    with self.assertRaises(ValueError):
                        self.skill(entities)

    def test_todo_skill_show_list_api_errors(self):
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

        entities = {"action": "show"}

        for error, expected_response in parameters:
            with self.subTest(error=error, expected_response=expected_response):
                with patch("ace.skills.get_todos", side_effect=error):
                    self.assertEqual(self.skill(entities), expected_response)

    def test_todo_skill_add_task_api_errors(self):
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

        entities = {"action": "add", "task": "Task 5"}

        for error, expected_response in parameters:
            with self.subTest(error=error, expected_response=expected_response):
                with patch("ace.skills.add_todo", side_effect=error):
                    self.assertEqual(self.skill(entities), expected_response)


class TestSkillNews(unittest.TestCase):
    def setUp(self):
        self.skill = skills_dict["NEWS_SKILL"]

    @patch("ace.skills.get_news")
    def test_news_skill(self, mock_get_news):
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

        for entities, mock_news, expected_response in parameters:
            with self.subTest(entities=entities, expected_response=expected_response):
                mock_get_news.return_value = mock_news
                self.assertEqual(self.skill(entities), expected_response)

    @patch("ace.skills.get_news")
    def test_news_skill_api_errors(self, mock_get_news):
        parameters = [
            (
                Exception(),
                "Sorry, there was an error fetching news articles.",
            ),
        ]

        entities = {"topic": "technology"}

        for error, expected_response in parameters:
            with self.subTest(error=error, expected_response=expected_response):
                mock_get_news.side_effect = error
                self.assertEqual(self.skill(entities), expected_response)


if __name__ == "__main__":
    unittest.main()
