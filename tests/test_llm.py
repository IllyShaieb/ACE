"""test_llm.py: Unit tests for the LLM integration in the ACE program.

Ensures that the LLM API service is functioning correctly.
"""

import unittest
from unittest.mock import patch

from google.genai import types

from core.actions import ACTION_HANDLERS
from core.llm import GoogleGenAIService


@patch("core.llm.os.getenv", return_value="MOCK_API_KEY")
@patch("core.llm.genai.Client")
class TestGoogleGenAIService(unittest.TestCase):
    """Unit tests for the GoogleGenAIService class."""

    def setUp(self):
        """Set up the test case with a GoogleGenAIService instance."""
        self.system_persona = "MOCK_PERSONA"
        self.mock_chat_history = []

    def test_initialisation_failure_no_api_key(self, mock_client, mock_getenv):
        """Test that initialization fails if API key is truly missing."""
        mock_getenv.return_value = None
        with self.assertRaises(ValueError):
            GoogleGenAIService(
                model_name="models/gemini-2.5-flash",
                system_persona=self.system_persona,
            )

    def test_direct_text_response(self, mock_client, mock_getenv):
        """Test a simple query resulting in a conversational (text) response."""

        # Arrange
        expected_text = "The fastest terrestrial animal is the cheetah."

        service = GoogleGenAIService(
            model_name="models/gemini-2.5-flash",
            system_persona=self.system_persona,
            actions=ACTION_HANDLERS,
        )

        mock_response = types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(parts=[types.Part(text=expected_text)])
                )
            ]
        )
        mock_client.return_value.models.generate_content.return_value = mock_response

        # Act
        response = service(
            user_query="What is the fastest land animal?",
            chat_history=self.mock_chat_history,
        )

        # Assert
        self.assertEqual(response, expected_text)
        mock_client.return_value.models.generate_content.assert_called_once()

    def test_tool_calling_response_no_args(self, mock_client, mock_getenv):
        """Test a query that results in a tool call without arguments (e.g., getting the current time)."""

        # Arrange
        expected_text = "What time is it?"
        service = GoogleGenAIService(
            model_name="models/gemini-2.5-flash",
            system_persona=self.system_persona,
            actions=ACTION_HANDLERS,
        )

        mock_response = types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(parts=[types.Part(text=expected_text)])
                )
            ]
        )
        mock_client.return_value.models.generate_content.return_value = mock_response

        # Act
        response = service(
            user_query="What time is it?",
            chat_history=self.mock_chat_history,
        )

        # Assert
        self.assertEqual(response, expected_text)
        mock_client.return_value.models.generate_content.assert_called_once()

    def test_tool_calling_response_with_args(self, mock_client, mock_getenv):
        """Test a query that results in a tool call with arguments (e.g., getting weather for a location)."""

        # Arrange
        expected_text = "The current weather in London is 15°C with light rain."
        service = GoogleGenAIService(
            model_name="models/gemini-2.5-flash",
            system_persona=self.system_persona,
            actions=ACTION_HANDLERS,
        )

        mock_response = types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(parts=[types.Part(text=expected_text)])
                )
            ]
        )
        mock_client.return_value.models.generate_content.return_value = mock_response

        # Act
        response = service(
            user_query="What's the weather like in London?",
            chat_history=self.mock_chat_history,
        )

        # Assert
        self.assertEqual(response, expected_text)
        mock_client.return_value.models.generate_content.assert_called_once()


if __name__ == "__main__":
    unittest.main()
