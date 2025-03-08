"""test_agents.py: Tests for the agents module in the ACE program.

Ensures that the agents in the ACE program work as expected, and that
the responses generated are correct.
"""

import unittest

from brain.agent import ACEAgent


class TestACEAgent(unittest.TestCase):
    """Tests for the ACEAgent class in the agents module."""

    def test_query(self):
        """Test the query method of the ACEAgents class."""
        ace_model = ACEAgent()

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
