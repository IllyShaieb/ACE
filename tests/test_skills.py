import unittest

from ace import skills_dict


class TestSkillDummy(unittest.TestCase):
    def setUp(self):
        self.skill = skills_dict["DUMMY_SKILL"]

    def test_dummy_skill_no_entities(self):
        self.assertEqual(self.skill(), "This is a dummy skill. It does nothing.")

    def test_dummy_skill_with_entities(self):
        self.assertEqual(
            self.skill(entities=["TEST"]),
            "This dummy skill has the following entities: ['TEST']",
        )

    def test_greeting_skill(self):
        self.assertEqual(
            skills_dict["GREETING_SKILL"](),
            "Hello! How can I help you?",
        )

    def test_farewell_skill(self):
        self.assertEqual(
            skills_dict["FAREWELL_SKILL"](),
            "Goodbye!",
        )

    def test_who_are_you_skill(self):
        expected = [
            "I'm ACE, your Artificial Consciousness Engine.",
            "I'm here to help with things and tell you what's going on.",
            "You can ask me to do stuff for you, or just chat with me!",
        ]
        self.assertEqual(skills_dict["WHO_ARE_YOU_SKILL"](), " ".join(expected))


if __name__ == "__main__":
    unittest.main()
