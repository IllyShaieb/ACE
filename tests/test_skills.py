import os
import random
import unittest
from unittest.mock import patch

from dotenv import load_dotenv
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


if __name__ == "__main__":
    unittest.main()
