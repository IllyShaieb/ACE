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
        self.assertEqual(processed, "this is a dummy user input")


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


class TestExtractEntities(unittest.TestCase):
    def test_extract_entities_DUMMY_SKILL(self):
        parameters = [
            ("run dummy skill", "DUMMY_SKILL", []),
            ("run dummy skill with 1", "DUMMY_SKILL", ["1"]),
            ("run dummy skill with 1 and 2", "DUMMY_SKILL", ["1", "2"]),
        ]

        for text, intent, expected in parameters:
            with self.subTest(text=text, intent=intent, expected=expected):
                entities = extract_entities(text, intent)
                self.assertEqual(entities, expected)


class TestSelectSkill(unittest.TestCase):
    def test_select_skill(self):
        skill = select_skill("DUMMY_SKILL")
        self.assertEqual(skill, skills_dict["DUMMY_SKILL"])


if __name__ == "__main__":
    unittest.main()
