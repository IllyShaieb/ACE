"""test_models.py: Tests for the models module in the ACE program.

Ensures that the models in the ACE program work as expected, and that
the responses generated are correct.
"""

import unittest

from brain.models import ACEModel


class TestACEModel(unittest.TestCase):
    """Tests for the ACEModel class in the models module."""

    def test_query(self):
        """Test the query method of the ACEModel class."""
        ace_model = ACEModel()

        scenarios = [
            ("", "Sorry, I don't understand.", "Check for empty input"),
            (" ", "Sorry, I don't understand.", "Check for whitespace input"),
        ]

        for user_input, expected_response, scenario_desc in scenarios:
            with self.subTest(scenario_desc):
                response = ace_model.query(user_input)
                self.assertEqual(response, expected_response)


if __name__ == "__main__":
    unittest.main()
