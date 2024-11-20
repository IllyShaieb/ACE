"""
This module contains unit tests for the `brain` module of the ACE digital assistant.

It includes test cases for the following functions:

- `get_user_input`: Tests the function that gets user input.
- `process_user_input`: Tests the function that processes user input.
- `recognise_intent`: Tests the function that recognises intents from user input.
- `extract_entities`: Tests the function that extracts entities from user input.
- `select_skill`: Tests the function that selects the appropriate skill based on the intent.

These tests ensure that the core logic of the ACE brain is functioning correctly
and can effectively handle user input, recognise intents, extract entities,
and select the appropriate skills.
"""

import unittest
from unittest.mock import patch

from ace import skills_dict
from ace.brain import (
    extract_entities,
    get_user_input,
    process_user_input,
    recognise_intent,
    select_skill,
)


class TestGetInput(unittest.TestCase):
    """Tests for retrieving user input.

    The purpose of these tests is to ensure that the various functions that
    allow the ACE digital assistant to receive user input are working correctly.
    """

    def test_get_user_input(self):
        """Test the `get_user_input` function returns the words given by the user."""

        # Need to mock the built-in `input` function to simulate user input
        with patch("builtins.input", return_value="This is a dummy user input."):
            self.assertEqual(get_user_input(), "This is a dummy user input.")


class TestProcessInput(unittest.TestCase):
    """Tests for processing user input.

    The purpose of these tests is to ensure that various functions that
    allow the ACE digital assistant to process user input are working correctly.
    """

    def test_process_user_input(self):
        """Test the `process_user_input` function correctly returns the processed input."""
        processed = process_user_input("This is a dummy user input.")
        self.assertEqual(processed, "this is a dummy user input.")


class TestRecogniseIntent(unittest.TestCase):
    """Tests for recognising user intent.

    The purpose of these tests is to ensure that the ACE digital assistant can
    correctly recognise the intent of the user input based on the given input.
    """

    def test_recognise_intent_DUMMY_SKILL(self):
        """Test the `recognise_intent` function for the DUMMY_SKILL intent."""

        # Set up the example sentences
        parameters = ["run dummy skill"]

        # Loop through the examples sentences and check the intent
        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "DUMMY_SKILL")

    def test_recognise_intent_GREETING_SKILL(self):
        """Test the `recognise_intent` function for the GREETING_SKILL intent."""

        # Set up the example sentences
        parameters = [
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        ]

        # Loop through the examples sentences and check the intent
        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "GREETING_SKILL")

    def test_recognise_intent_FAREWELL_SKILL(self):
        """Test the `recognise_intent` function for the FAREWELL_SKILL intent."""

        # Set up the example sentences
        parameters = ["goodbye", "bye", "good bye"]

        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "FAREWELL_SKILL")

    def test_recognise_intent_WHO_ARE_YOU_SKILL(self):
        """Test the `recognise_intent` function for the WHO_ARE_YOU_SKILL intent."""

        # Set up the example sentences
        parameters = ["who are you", "what are you"]

        # Loop through the examples sentences and check the intent
        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "WHO_ARE_YOU_SKILL")

    def test_recognise_intent_HOW_ARE_YOU_SKILL(self):
        """Test the `recognise_intent` function for the HOW_ARE_YOU_SKILL intent."""

        # Set up the example sentences
        parameters = ["how are you"]

        # Loop through the examples sentences and check the intent
        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "HOW_ARE_YOU_SKILL")

    def test_recognise_intent_GET_WEATHER_SKILL(self):
        """Test the `recognise_intent` function for the GET_WEATHER_SKILL intent."""

        # Set up the example sentences
        parameters = [
            "what is the current weather",
            "what is the weather today",
            "weather today",
            "current weather",
            "current weather in London",
            "weather today in London",
            "current weather in New York",
            "weather today in -44.10435,146.84735",
            "current weather in -44.10435,146.84735",
            "current weather at -44.10435,146.84735",
            "weather today at -44.10435,146.84735",
            "what is the weather tomorrow",
            "what is the weather tomorrow in London",
            "what is the weather tomorrow in New York",
            "what is the weather tomorrow in -44.10435,146.847",
            "tomorrow's weather",
            "tomorrow's weather in London",
            "tomorrow's weather in New York",
            "tomorrow's weather in -44.10435,146.847",
            "weather tomorrow",
            "weather tomorrow at -44.10435,146.847",
        ]

        # Loop through the examples sentences and check the intent
        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "GET_WEATHER_SKILL")

    def test_recognise_intent_TELL_TIME_SKILL(self):
        """Test the `recognise_intent` function for the TELL_TIME_SKILL intent."""

        # Set up the example sentences
        parameters = [
            "what time is it",
            "tell me the time",
            "current time",
            "what time will it be in 5 minutes",
            "what time will it be in 2 hours",
            "what is the time now",
            "give me the time in 10 seconds",
        ]

        # Loop through the examples sentences and check the intent
        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "TELL_TIME_SKILL")

    def test_recognise_intent_TODO_SKILL(self):
        """Test the `recognise_intent` function for the TODO_SKILL intent."""

        # Set up the example sentences
        list_name_singular = ["todo", "task", "to-do", "to do"]
        list_name_plural = ["todos", "tasks", "to-dos", "to dos"]

        parameters = [
            ["{0} list", [*list_name_singular, *list_name_plural]],
            ["{0}", [*list_name_plural]],
            ["show {0} list", [*list_name_singular, *list_name_plural]],
            ["show me my {0} list", [*list_name_singular, *list_name_plural]],
            ["give me my {0} list", [*list_name_singular, *list_name_plural]],
            ["give my {0} list", [*list_name_singular, *list_name_plural]],
            ["give {0} list", [*list_name_singular, *list_name_plural]],
            ["what's on my {0} list", [*list_name_singular, *list_name_plural]],
            ["what do I have to do", []],
            ["what are my {0}", [*list_name_plural]],
            ["add a task to my {0} list", [*list_name_singular, *list_name_plural]],
            ["add buy milk to my {0} list", [*list_name_singular, *list_name_plural]],
            [
                "add take out the trash to my {0} list",
                [*list_name_singular, *list_name_plural],
            ],
            [
                "add show the ace project to team to my {0} list",
                [*list_name_singular, *list_name_plural],
            ],
            [
                "add show ace to the world to my {0} list",
                [*list_name_singular, *list_name_plural],
            ],
        ]

        # Loop through the examples sentences and check the intent
        for task, lists in parameters:
            for list_name in lists:
                for list_name in lists:
                    text = task.format(list_name)
                    with self.subTest(text=text):
                        intent = recognise_intent(text)
                        self.assertEqual(intent, "TODO_SKILL")

    def test_recognise_intent_NEWS_SKILL(self):
        """Test the `recognise_intent` function for the NEWS_SKILL intent."""

        # Set up the example sentences
        parameters = [
            "show me the news",
            "get me the news",
            "show the news",
            "get the news",
            "show news",
            "get news",
            "get me the news about technology",
            "show me the news about sports",
            "get me news about politics",
            "show me news about science",
            "get the news about technology",
            "show the news about sports",
            "what's in the news",
            "what's in the news about cheese",
            "what is in the news",
            "what is in the news about python",
            "what is the news today",
            "what is the news about technology today",
        ]

        # Loop through the examples sentences and check the intent
        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "NEWS_SKILL")


class TestExtractEntities(unittest.TestCase):
    """Tests for extracting entities from user input.

    The purpose of these tests is to ensure that the ACE digital assistant can
    correctly extract entities from the user input based on the given intent.
    """

    def test_extract_entities_DUMMY_SKILL(self):
        """Test the `extract_entities` function for the DUMMY_SKILL intent."""

        # Set up the example sentences
        parameters = [
            ("run dummy skill", "DUMMY_SKILL", {}),
            ("run dummy skill with 1", "DUMMY_SKILL", {"group1": "1"}),
            (
                "run dummy skill with 1 and 2",
                "DUMMY_SKILL",
                {"group1": "1", "group2": "2"},
            ),
        ]

        # Loop through the examples sentences and check the entities
        for text, intent, expected in parameters:
            with self.subTest(text=text, intent=intent, expected=expected):
                entities = extract_entities(text, intent)
                self.assertEqual(entities, expected)

    def test_extract_entities_GET_WEATHER_SKILL(self):
        """Test the `extract_entities` function for the GET_WEATHER_SKILL intent."""

        # Set up the example sentences
        intent = "GET_WEATHER_SKILL"
        parameters = [
            ("current weather", {"timeframe": "current"}),
            (
                "current weather in London",
                {"timeframe": "current", "location": "London"},
            ),
            (
                "current weather in New York",
                {"timeframe": "current", "location": "New York"},
            ),
            ("weather today", {"timeframe": "today"}),
            ("weather today in London", {"timeframe": "today", "location": "London"}),
            (
                "weather today in New York",
                {"timeframe": "today", "location": "New York"},
            ),
            ("weather in London today", {"timeframe": "today", "location": "London"}),
            (
                "weather in New York today",
                {"timeframe": "today", "location": "New York"},
            ),
            (
                "current weather in -44.10435,146.84735",
                {"timeframe": "current", "location": "-44.10435,146.84735"},
            ),
            (
                "weather today in -44.10435,146.84735",
                {"timeframe": "today", "location": "-44.10435,146.84735"},
            ),
            (
                "current weather at -44.10435,146.84735",
                {"timeframe": "current", "location": "-44.10435,146.84735"},
            ),
            ("weather tomorrow", {"timeframe": "tomorrow"}),
            (
                "weather tomorrow in London",
                {"timeframe": "tomorrow", "location": "London"},
            ),
            (
                "weather tomorrow in New York",
                {"timeframe": "tomorrow", "location": "New York"},
            ),
            (
                "weather tomorrow in -44.10435,146.84735",
                {"timeframe": "tomorrow", "location": "-44.10435,146.84735"},
            ),
            ("tomorrow's weather", {"timeframe": "tomorrow"}),
            (
                "tomorrow's weather in London",
                {"timeframe": "tomorrow", "location": "London"},
            ),
            (
                "tomorrow's weather in New York",
                {"timeframe": "tomorrow", "location": "New York"},
            ),
            (
                "tomorrow's weather in -44.10435,146.84735",
                {"timeframe": "tomorrow", "location": "-44.10435,146.84735"},
            ),
            (
                "weather tomorrow at -44.10435,146.84735",
                {"timeframe": "tomorrow", "location": "-44.10435,146.84735"},
            ),
            (
                "tomorrow's weather at -44.10435,146.84735",
                {"timeframe": "tomorrow", "location": "-44.10435,146.84735"},
            ),
        ]

        # Loop through the examples sentences and check the entities
        for text, expected in parameters:
            with self.subTest(text=text, expected=expected):
                entities = extract_entities(text, intent)
                # entities can be in any order
                self.assertEqual(entities, expected)

    def test_extract_entities_TELL_TIME_SKILL(self):
        """Test the `extract_entities` function for the TELL_TIME_SKILL intent."""

        # Set the intent and example sentences
        intent = "TELL_TIME_SKILL"

        parameters = [
            (
                "what time will it be in 5 minutes",
                {"timevalue": "5", "timeunit": "minute"},
            ),
            (
                "what time will it be in 2 hours",
                {"timevalue": "2", "timeunit": "hour"},
            ),
            (
                "what time will it be in 10 seconds",
                {"timevalue": "10", "timeunit": "second"},
            ),
            (
                "tell me the time",
                {},
            ),
        ]

        # Loop through the examples sentences and check the entities
        for text, expected in parameters:
            with self.subTest(text=text, expected=expected):
                entities = extract_entities(text, intent)
                self.assertEqual(entities, expected)

    def test_extract_entities_TODO_SKILL(self):
        """Test the `extract_entities` function for the TODO_SKILL intent."""

        # Set the intent and example sentences
        intent = "TODO_SKILL"

        list_name_singular = ["todo", "task", "to-do", "to do"]
        list_name_plural = ["todos", "tasks", "to-dos", "to dos"]

        parameters = [
            ("{0} list", [*list_name_singular, *list_name_plural], {}),
            ("{0}", [*list_name_plural], {}),
            (
                "show {0} list",
                [*list_name_singular, *list_name_plural],
                {"action": "show"},
            ),
            (
                "show {0}",
                [*list_name_plural],
                {"action": "show"},
            ),
            (
                "show my {0} list",
                [*list_name_singular, *list_name_plural],
                {"action": "show"},
            ),
            (
                "show me my {0} list",
                [*list_name_singular, *list_name_plural],
                {"action": "show"},
            ),
            (
                "give me my {0} list",
                [*list_name_singular, *list_name_plural],
                {"action": "give"},
            ),
            (
                "give my {0} list",
                [*list_name_singular, *list_name_plural],
                {"action": "give"},
            ),
            (
                "give {0} list",
                [*list_name_singular, *list_name_plural],
                {"action": "give"},
            ),
            (
                "what's on my {0} list",
                [*list_name_singular, *list_name_plural],
                {"action": "what"},
            ),
            ("what do I have to do", [], {"action": "what"}),
            (
                "what are my {0}",
                [*list_name_plural],
                {"action": "what"},
            ),
            (
                "add a task to my {0} list",
                [*list_name_singular, *list_name_plural],
                {"action": "add"},
            ),
            (
                "add buy milk to my {0} list",
                [*list_name_singular, *list_name_plural],
                {"action": "add", "task": "buy milk"},
            ),
            (
                "add take out the trash to my {0} list",
                [*list_name_singular, *list_name_plural],
                {"action": "add", "task": "take out the trash"},
            ),
            (
                "add show the ace project to my team to my {0} list",
                [*list_name_singular, *list_name_plural],
                {"action": "add", "task": "show the ace project to my team"},
            ),
        ]

        # Loop through the examples sentences and check the entities
        for text, lists, expected in parameters:
            for list_name in lists:
                text = text.format(list_name)
                with self.subTest(text=text, expected=expected):
                    entities = extract_entities(text, intent)
                    self.assertEqual(entities, expected)

    def test_extract_entities_NEWS_SKILL(self):
        """Test the `extract_entities` function for the NEWS_SKILL intent."""

        # Set the intent and example sentences
        intent = "NEWS_SKILL"

        parameters = [
            ("show me the news", {}),
            ("get me the news", {}),
            ("show the news", {}),
            ("get the news", {}),
            ("show news", {}),
            ("get news", {}),
            ("get me the news about technology", {"topic": "technology"}),
            ("show me the news about sports", {"topic": "sports"}),
            ("get me news about politics", {"topic": "politics"}),
            ("show me news about science", {"topic": "science"}),
            ("get the news about technology", {"topic": "technology"}),
            ("show the news about sports", {"topic": "sports"}),
            ("what's in the news", {}),
            ("what's in the news about cheese", {"topic": "cheese"}),
            ("what is in the news", {}),
            ("what is in the news about python", {"topic": "python"}),
            ("what is the news today", {}),
            ("what is the news about technology today", {"topic": "technology"}),
        ]

        # Loop through the examples sentences and check the entities
        for text, expected in parameters:
            with self.subTest(text=text, expected=expected):
                entities = extract_entities(text, intent)
                self.assertEqual(entities, expected)


class TestSelectSkill(unittest.TestCase):
    """Tests for selecting the appropriate skill.

    The purpose of these tests is to ensure that the ACE digital assistant can
    correctly select the appropriate skill based on the intent recognised from
    the user input.
    """

    def test_select_skill(self):
        """Test the `select_skill` function by using the DUMMY_SKILL, which
        should always be available in the skills dictionary
        """
        skill = select_skill("DUMMY_SKILL")
        self.assertEqual(skill, skills_dict["DUMMY_SKILL"])


if __name__ == "__main__":
    unittest.main()
