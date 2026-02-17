"""core.models: This module defines the model classes for the ACE application, responsible for managing
data and business logic."""


class MinimumViableModel:
    """A simple model implementation that processes user queries and returns responses based on
    basic keyword recognition."""

    async def process_query(self, query: str) -> str:
        """Process a user query and return a response.

        Args:
            query (str): The user query to process.
        """
        cleaned_query = query.strip().lower()

        truth_map = {
            "greeting": (
                any(greet in cleaned_query for greet in ["hello", "hi", "hey"]),
                "Hello! How can I assist you today?",
            ),
            "help": (
                "help" in cleaned_query,
                "Sure! You can ask me anything or type 'exit' to quit.",
            ),
            "meaning of life": (
                "meaning of life" in cleaned_query,
                "42 is the answer to the ultimate question of life, the universe, and everything.",
            ),
        }

        for key, (condition, response) in truth_map.items():
            if condition:
                return response
        return "I'm not sure how to respond to that."
