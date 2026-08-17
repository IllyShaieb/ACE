"""Ensure that the model processes text correctly and returns expected responses."""

import json
from unittest.mock import MagicMock

import pytest
from groq import Groq

from src.model import GroqModel
from src.tools import Tool


class MockTool:
    """A mock tool for testing purposes."""

    name = "mock_tool"
    description = "A mock tool for testing."
    parameters = {}

    def execute(self, *args, **kwargs):
        return "Mock tool executed"

    def to_groq_spec(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
            "required": [],
        }


def test_model_process_text_with_mocked_groq():
    """Test that the model processes text correctly using a mocked Groq client."""
    # ARRANGE: Create a mock Groq client, expected response and a GroqModel instance
    mock_groq = MagicMock(spec=Groq)
    mock_message = MagicMock()
    mock_message.content = "Processed text"
    mock_message.tool_calls = None
    mock_groq.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=mock_message)]
    )

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
    mock_message = MagicMock()
    mock_message.content = None
    mock_message.tool_calls = None
    mock_groq.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=mock_message)]
    )

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


def test_model_passes_tools_to_groq():
    """Test that the model correctly passes tools to the Groq client."""
    # ARRANGE: Create a mock Groq client and a list of tools
    mock_groq = MagicMock(spec=Groq)

    tool_call = MagicMock(id="call_123")
    tool_call.function.name = "mock_tool"
    tool_call.function.arguments = json.dumps({})

    first_message = MagicMock(content=None, tool_calls=[tool_call])
    second_message = MagicMock(
        content="The tool output was processed.", tool_calls=None
    )

    mock_groq.chat.completions.create.side_effect = [
        MagicMock(choices=[MagicMock(message=first_message)]),
        MagicMock(choices=[MagicMock(message=second_message)]),
    ]

    tools = [MockTool()]
    model = GroqModel(groq=mock_groq, tools=tools)  # type: ignore

    # ACT: Call process_text with a sample input
    input_text = "Run mock tool"
    result = model.process_text(input_text)

    # ASSERT: Verify that the Groq client was called with the correct tools
    assert (
        result == "The tool output was processed."
    ), "The model should return the final processed response after tool execution."
    assert (
        mock_groq.chat.completions.create.call_count == 2
    ), "The Groq client should be called twice: once for the initial request and once after tool execution."
    assert mock_groq.chat.completions.create.call_args_list[0][1]["tools"] == [
        t.to_groq_spec() for t in tools
    ], "The tools passed to the Groq client should match the provided tools."
