import unittest

from ace.skills import skills


class TestSkillDummy(unittest.TestCase):
    def setUp(self):
        self.skill = skills()["dummy"]

    def test_dummy_skill_no_entities(self):
        assert self.skill() == "This is a dummy skill. It does nothing."

    def test_dummy_skill_with_entities(self):
        assert (
            self.skill(entities=["TEST"])
            == "This dummy skill has the following entities: ['TEST']"
        )


if __name__ == "__main__":
    unittest.main()
