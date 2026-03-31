"""tests.models.test_base: Test the MinimumViableModel class to ensure it processes queries correctly
and returns expected responses."""

import unittest
from core.models.base import MinimumViableModel


class TestMinimumViableModel(unittest.IsolatedAsyncioTestCase):
    """Test the MinimumViableModel's ability to process queries and return responses."""

    async def asyncSetUp(self):
        """Set up common test components."""
        self.model = MinimumViableModel()

    async def test_process_query_returns_expected_response(self):
        """Verify that `process_query()` returns the expected response for a given query."""
        # ARRANGE: Define a sample queries and expected responses
        test_cases = [
            (
                "Hello ACE",
                "Hello! How can I assist you today?",
                "Test greeting with 'Hello'",
            ),
            (
                "Hi there",
                "Hello! How can I assist you today?",
                "Test greeting with 'Hi'",
            ),
            ("Hey!", "Hello! How can I assist you today?", "Test greeting with 'Hey'"),
            (
                "Can you help me?",
                "Sure! You can ask me anything or type 'exit' to quit.",
                "Test help query",
            ),
            (
                "What is the meaning of life?",
                "42 is the answer to the ultimate question of life, the universe, and everything.",
                "Test meaning of life query",
            ),
            (
                "What is your name?",
                "I'm not sure how to respond to that.",
                "Test unrecognized query",
            ),
        ]

        for query, expected_response, description in test_cases:
            with self.subTest(msg=description):
                # ACT: Process the query using the model
                response = await self.model.process_query(query)

                # ASSERT: Verify the response matches the expected output
                self.assertEqual(response, expected_response)


if __name__ == "__main__":
    unittest.main()
