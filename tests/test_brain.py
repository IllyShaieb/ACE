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
    def test_get_user_input(self):
        with patch("builtins.input", return_value="This is a dummy user input."):
            self.assertEqual(get_user_input(), "This is a dummy user input.")


class TestProcessInput(unittest.TestCase):
    def test_process_user_input(self):
        processed = process_user_input("This is a dummy user input.")
        self.assertEqual(processed, "this is a dummy user input.")


class TestRecogniseIntent(unittest.TestCase):

    def test_recognise_intent_DUMMY(self):
        parameters = ["run dummy skill"]

        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "DUMMY_SKILL")

    def test_recognise_intent_GREETING(self):
        parameters = [
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        ]

        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "GREETING_SKILL")

    def test_recognise_intent_FAREWELL(self):
        parameters = ["goodbye", "bye", "good bye"]

        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "FAREWELL_SKILL")

    def test_who_are_you_skill(self):
        parameters = ["who are you", "what are you"]

        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "WHO_ARE_YOU_SKILL")

    def test_how_are_you_skill(self):
        parameters = ["how are you"]

        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "HOW_ARE_YOU_SKILL")

    def test_get_weather_skill(self):
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

        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "GET_WEATHER_SKILL")

    def test_tell_time_skill(self):
        parameters = [
            "what time is it",
            "tell me the time",
            "current time",
            "what time will it be in 5 minutes",
            "what time will it be in 2 hours",
            "what is the time now",
            "give me the time in 10 seconds",
        ]

        for parameter in parameters:
            with self.subTest(parameter=parameter):
                intent = recognise_intent(parameter)
                self.assertEqual(intent, "TELL_TIME_SKILL")

    def test_todo_skill(self):
        list_name_singular = ["todo", "task", "to-do", "to do"]
        list_name_plural = ["todos", "tasks", "to-dos", "to dos"]

        parameters = [
            ["show {0} list", [*list_name_singular, *list_name_plural]],
            ["show me my {0} list", [*list_name_singular, *list_name_plural]],
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

        for task, lists in parameters:
            for list_name in lists:
                for list_name in lists:
                    text = task.format(list_name)
                    with self.subTest(text=text):
                        intent = recognise_intent(text)
                        self.assertEqual(intent, "TODO_SKILL")


class TestExtractEntities(unittest.TestCase):
    def test_extract_entities_DUMMY_SKILL(self):
        parameters = [
            ("run dummy skill", "DUMMY_SKILL", {}),
            ("run dummy skill with 1", "DUMMY_SKILL", {"group1": "1"}),
            (
                "run dummy skill with 1 and 2",
                "DUMMY_SKILL",
                {"group1": "1", "group2": "2"},
            ),
        ]

        for text, intent, expected in parameters:
            with self.subTest(text=text, intent=intent, expected=expected):
                entities = extract_entities(text, intent)
                self.assertEqual(entities, expected)

    def test_extract_entities_GET_WEATHER_SKILL(self):
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

        for text, expected in parameters:
            with self.subTest(text=text, expected=expected):
                entities = extract_entities(text, intent)
                # entities can be in any order
                self.assertEqual(entities, expected)

    def test_extract_entities_TELL_TIME_SKILL(self):
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

        for text, expected in parameters:
            with self.subTest(text=text, expected=expected):
                entities = extract_entities(text, intent)
                self.assertEqual(entities, expected)

    def test_extract_entities_TODO_SKILL(self):
        intent = "TODO_SKILL"

        list_name_singular = ["todo", "task", "to-do", "to do"]
        list_name_plural = ["todos", "tasks", "to-dos", "to dos"]

        parameters = [
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

        for text, lists, expected in parameters:
            for list_name in lists:
                text = text.format(list_name)
                with self.subTest(text=text, expected=expected):
                    entities = extract_entities(text, intent)
                    self.assertEqual(entities, expected)


class TestSelectSkill(unittest.TestCase):
    def test_select_skill(self):
        skill = select_skill("DUMMY_SKILL")
        self.assertEqual(skill, skills_dict["DUMMY_SKILL"])


if __name__ == "__main__":
    unittest.main()
