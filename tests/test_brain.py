import unittest
from unittest.mock import patch

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
            assert get_user_input() == "This is a dummy user input."


class TestProcessInput(unittest.TestCase):
    def test_process_user_input(self):
        processed = process_user_input("This is a dummy user input.")
        assert processed == "this is a dummy user input"


class TestRecogniseIntent(unittest.TestCase):
    def test_recognise_intent(self):
        processed_input = "this is a dummy user input"
        intent = recognise_intent(processed_input)
        assert intent == "DUMMY"


class TestExtractEntities(unittest.TestCase):
    def test_extract_entities(self):
        processed_input = "this is a dummy user input"
        entities = extract_entities(processed_input)
        assert entities == []


class TestSelectSkill(unittest.TestCase):
    def test_select_skill(self):
        skill = select_skill("DUMMY")
        assert skill == "DUMMY_SKILL"

    def test_select_skill_unknown(self):
        skill = select_skill("UNKNOWN")
        assert skill == "UNKNOWN_SKILL"


if __name__ == "__main__":
    unittest.main()
