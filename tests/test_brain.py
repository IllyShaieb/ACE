import unittest
from unittest.mock import patch

from ace import skills_config
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
    def test_recognise_intent(self):
        processed_input = "this is a dummy user input"
        intent = recognise_intent(processed_input)
        self.assertEqual(intent, "DUMMY_SKILL")


class TestExtractEntities(unittest.TestCase):
    def test_extract_entities(self):
        processed_input = "this is a dummy user input"
        entities = extract_entities(processed_input)
        self.assertEqual(entities, [])


class TestSelectSkill(unittest.TestCase):
    def test_select_skill(self):
        skill = select_skill("DUMMY_SKILL")
        self.assertEqual(skill, skills_config["DUMMY_SKILL"])


if __name__ == "__main__":
    unittest.main()
