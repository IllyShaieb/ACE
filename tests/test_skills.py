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


if __name__ == "__main__":
    unittest.main()
