import unittest

from ace import skills_config


class TestSkillDummy(unittest.TestCase):
    def setUp(self):
        self.skill = skills_config["DUMMY_SKILL"]

    def test_dummy_skill_no_entities(self):
        self.assertEqual(self.skill(), "This is a dummy skill. It does nothing.")

    def test_dummy_skill_with_entities(self):
        self.assertEqual(
            self.skill(entities=["TEST"]),
            "This dummy skill has the following entities: ['TEST']",
        )


if __name__ == "__main__":
    unittest.main()
