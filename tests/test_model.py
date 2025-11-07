"""test_model.py: Unit tests for the model class."""

import unittest
from unittest.mock import Mock, patch

from core.model import ACEModel


@patch("core.llm.os.getenv", return_value="MOCK_API_KEY")
@patch("core.llm.genai.Client")
class TestACEModel(unittest.TestCase):
    """Test cases for the ACEModel class."""

    def setUp(self):
        """Set up for each test case."""
        # Initialize the model
        self.ace_model = ACEModel()

        # Mock the external API service and its response
        self.mock_api_service = Mock(return_value="Mocked LLM Response")

        # Patch the model to use the mock service instead of the real one
        self.ace_model.api_service = self.mock_api_service

    def test_model_call(self, mock_client: Mock, mock_getenv: Mock):
        """Test that the model class correctly calls the API service."""
        # Arrange
        user_input = "Hello"
        chat_history = []

        # Act
        response = self.ace_model(user_input, chat_history)

        # Assert
        self.mock_api_service.assert_called_once_with(user_input, chat_history)
        self.assertEqual(response, "Mocked LLM Response")

    def test_model_call_with_history(self, mock_client: Mock, mock_getenv: Mock):
        """Test that the model class passes history to the API service."""
        # Arrange
        user_input = "Who are you?"
        chat_history = [{"role": "user", "text": "Hello"}]

        # Act
        response = self.ace_model(user_input, chat_history)

        # Assert
        self.mock_api_service.assert_called_once_with(user_input, chat_history)
        self.assertEqual(response, "Mocked LLM Response")


if __name__ == "__main__":
    unittest.main()
