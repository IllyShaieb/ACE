"""tests.tools.test_text: Ensure the text manipulation tools function as expected."""

import unittest

from core.tools import text


class TestCharacterCounterTool(unittest.TestCase):
    """Test the CharacterCounterTool's ability to count characters in a given input string."""

    def setUp(self):
        """Set up common test components."""
        self.tool = text.CharacterCounterTool()

    def test_execute_counts_characters(self):
        """Verify that `execute()` correctly counts the number of characters in the input string."""
        # ARRANGE: Define the input string and expected character count
        test_cases = [
            {
                "input_string": "",
                "with_spaces": True,
                "character": None,
                "expected_count": 0,
                "description": "Empty string should return 0.",
            },
            {
                "input_string": "Hello",
                "with_spaces": True,
                "character": None,
                "expected_count": 5,
                "description": "Simple word should return correct count.",
            },
            {
                "input_string": "ACE - The Artificial Consciousness Engine",
                "with_spaces": True,
                "character": None,
                "expected_count": 41,
                "description": "Longer sentence should return correct count.",
            },
            {
                "input_string": "   Leading and trailing spaces   ",
                "with_spaces": True,
                "character": None,
                "expected_count": 33,
                "description": "String with spaces should return correct count.",
            },
            {
                "input_string": "Count only letters",
                "with_spaces": False,
                "character": None,
                "expected_count": 16,
                "description": "Count characters without spaces.",
            },
            {
                "input_string": "Count only 'o' characters",
                "with_spaces": True,
                "character": "o",
                "expected_count": 3,
                "description": "Count only specific character 'o'.",
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["description"]):
                # ACT: Execute the tool with the input string
                result = self.tool.execute(
                    input_string=case["input_string"],
                    with_spaces=case["with_spaces"],
                    character=case["character"],
                )

                # ASSERT: Verify the result matches the expected character count
                self.assertIsInstance(result, int)
                self.assertEqual(result, case["expected_count"])


if __name__ == "__main__":
    unittest.main()
