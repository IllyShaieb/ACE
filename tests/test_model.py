"""Ensure that the model processes text correctly and returns expected responses."""

from unittest.mock import MagicMock

import pytest
from groq import Groq

from src.model import GroqModel


def test_model_process_text_with_mocked_groq():
    """Test that the model processes text correctly using a mocked Groq client."""
    # ARRANGE: Create a mock Groq client, expected response and a GroqModel instance
    mock_groq = MagicMock(spec=Groq)
    mock_chat_completion = MagicMock()
    mock_chat_completion.choices = [MagicMock()]
    mock_chat_completion.choices[0].message.content = "Processed text"
    mock_groq.chat.completions.create.return_value = mock_chat_completion

    model = GroqModel(groq=mock_groq, model_name="openai/gpt-oss-120b")

    # ACT: Call the process_text method with a sample input
    input_text = "Hello, World!"
    result = model.process_text(input_text)

    # ASSERT: Verify that the result is as expected and that the Groq client was called correctly
    assert (
        result == "Processed text"
    ), "The model should return the processed text from the mocked Groq client."
    mock_groq.chat.completions.create.assert_called_once_with(
        model="openai/gpt-oss-120b", messages=model.messages
    )


def test_model_process_text_with_no_response():
    """Test that the model handles cases where no response is received from the Groq client."""
    # ARRANGE: Create a mock Groq client that returns no response
    mock_groq = MagicMock(spec=Groq)
    mock_chat_completion = MagicMock()
    mock_chat_completion.choices = [MagicMock()]
    mock_chat_completion.choices[0].message.content = None  # Simulate no response
    mock_groq.chat.completions.create.return_value = mock_chat_completion

    model = GroqModel(groq=mock_groq)

    # ACT: Call the process_text method with a sample input
    input_text = "Hello, World!"
    result = model.process_text(input_text)

    # ASSERT: Verify that the result indicates no response was received
    assert (
        result == "No response received."
    ), "The model should return a message indicating no response was received."


def test_model_initialises_with_system_prompt():
    """Test that providing a system_prompt populates the initial message history."""
    # ARRANGE: Create a mock Groq client and a system prompt
    mock_groq = MagicMock(spec=Groq)
    system_prompt = "You are a helpful assistant."

    # ACT: Initialize the model with the system prompt
    model = GroqModel(groq=mock_groq, system_prompt=system_prompt)

    # ASSERT: Verify that the initial message history contains the system prompt
    assert len(model.messages) == 1, "The model should have one initial message."
    assert (
        model.messages[0]["role"] == "system"
    ), "The initial message should have the role 'system'."
    assert (
        model.messages[0]["content"] == system_prompt
    ), "The initial message content should match the provided system prompt."


def test_model_accumulates_conversation_history():
    """Test that process_text appends user and assistant messages to history."""
    # ARRANGE: Create a mock Groq client that returns a response
    mock_groq = MagicMock(spec=Groq)
    mock_chat_completion = MagicMock()
    mock_chat_completion.choices = [MagicMock()]
    mock_chat_completion.choices[0].message.content = "Response 1"
    mock_groq.chat.completions.create.return_value = mock_chat_completion

    model = GroqModel(groq=mock_groq)

    # ACT: Call process_text twice with different inputs
    model.process_text("Message 1")

    # ASSERT: Verify that the conversation history has two messages (user and assistant)
    assert len(model.messages) == 2, "The model should have two messages in history."
    assert (
        model.messages[0]["role"] == "user"
    ), "The first message should have the role 'user'."
    assert (
        model.messages[1]["role"] == "assistant"
    ), "The second message should have the role 'assistant'."


def test_model_process_error_handling():
    """Test that the model handles errors gracefully when the Groq client raises an exception."""
    # ARRANGE: Create a mock Groq client that raises an exception
    mock_groq = MagicMock(spec=Groq)
    mock_groq.chat.completions.create.side_effect = Exception("Simulated error")

    model = GroqModel(groq=mock_groq)

    # ACT & ASSERT: Verify RuntimeError is raised (wrapping the raw API error)
    with pytest.raises(RuntimeError) as exc_info:
        model.process_text("This will cause an error")

    assert "Model API error: Simulated error" in str(exc_info.value)

    # Verify that the user message was removed from history after the error
    assert len(model.messages) == 0, "History should be cleaned up on failure."
