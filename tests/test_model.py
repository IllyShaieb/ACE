"""Ensure that the model processes text correctly and returns expected responses."""

import json
from unittest.mock import MagicMock, call

import pytest
from groq import Groq

from src.model import GroqModel
from src.storage import ConversationStorage
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


def _create_mock_message(
    content: str | None, tool_calls: list[dict] | None = None
) -> MagicMock:
    """Helper function to create a mock message with specified content and tool calls.
    Args:
        content (str): The content of the mock message.
        tool_calls (list[dict] | None): A list of tool call dictionaries or None.

    Returns:
        MagicMock: A mock message object with the specified content and tool calls.
    """
    mock_message = MagicMock()
    mock_message.content = content
    mock_message.tool_calls = tool_calls
    return mock_message


def _create_mock_tool_call(
    call_id: str, function_name: str, arguments: dict
) -> MagicMock:
    """Helper to mock a tool call object.

    Args:
        call_id (str): The ID of the tool call.
        function_name (str): The name of the function being called.
        arguments (dict): The arguments for the function call.

    Returns:
        MagicMock: A mock tool call object with the specified properties.
    """
    tool_call = MagicMock()
    tool_call.id = call_id
    tool_call.function.name = function_name
    tool_call.function.arguments = json.dumps(arguments)
    return tool_call


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
        result == "I am not sure how to answer that."
    ), "The model should return a fallback message when no response is received from the Groq client."


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
    mock_chat_completion.choices[0].message.tool_calls = None
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


@pytest.mark.parametrize(
    "finish_reason, was_tool_call, expected_phrase",
    [
        ("content_filter", False, "unable to assist"),
        ("length", False, "cut short"),
        ("stop", True, "Action completed"),
        ("stop", False, "not sure how to answer"),
        (None, False, "not sure how to answer"),
    ],
)
def test_model_handles_specific_finish_reasons_when_content_is_none(
    finish_reason, was_tool_call, expected_phrase
):
    """Test that the model handles specific finish reasons when the content is None."""
    # ARRANGE: Create a mock Groq client that returns a message with no content
    mock_groq = MagicMock(spec=Groq)

    if was_tool_call:
        # First call triggers the tool
        tool_call = MagicMock(id="call_123")
        tool_call.function.name = "mock_tool"
        tool_call.function.arguments = json.dumps({})

        first_message = MagicMock(content=None, tool_calls=[tool_call])

        # Second call returns empty content with the given finish_reason
        second_choice = MagicMock()
        second_choice.message.content = None
        second_choice.message.tool_calls = None
        second_choice.finish_reason = finish_reason

        mock_groq.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=first_message)]),
            MagicMock(choices=[second_choice]),
        ]
        model = GroqModel(groq=mock_groq, tools=[MockTool()])
    else:
        choice = MagicMock()
        choice.message.content = None
        choice.message.tool_calls = None
        choice.finish_reason = finish_reason

        mock_groq.chat.completions.create.return_value = MagicMock(choices=[choice])
        model = GroqModel(groq=mock_groq)

    # ACT: Call process_text with a sample input
    input_text = "Hello, World!"
    result = model.process_text(input_text)

    # ASSERT: Verify that the result contains the expected phrase based on finish reason
    assert (
        expected_phrase in result
    ), f"The model should return a message indicating '{expected_phrase}' for finish reason '{finish_reason}'."


def test_groq_model_executes_multiple_parallel_tool_calls():
    """Verify GroqModel handles multiple tool calls in a single completion turn."""

    # ARRANGE: Create a mock Groq client that returns multiple tool calls
    mock_groq = MagicMock(spec=Groq)

    # Tool 1: clock, Tool 2: wolfram_alpha
    tool1 = MagicMock()
    tool1.name = "clock"
    tool1.execute.return_value = "2026-08-21T12:00:00"

    tool2 = MagicMock()
    tool2.name = "wolfram_alpha"
    tool2.execute.return_value = "Result: 42"

    # Turn 1: Model requests both tools
    call1 = _create_mock_tool_call("call_1", "clock", {})
    call2 = _create_mock_tool_call("call_2", "wolfram_alpha", {"query": "6 * 7"})
    resp_turn_1 = MagicMock()
    resp_turn_1.choices = [
        MagicMock(message=_create_mock_message(None, [call1, call2]))
    ]

    # Turn 2: Model synthesizes final text
    resp_turn_2 = MagicMock()
    resp_turn_2.choices = [
        MagicMock(
            message=_create_mock_message("The time is 12:00 and 6*7 is 42.", None)
        )
    ]

    mock_groq.chat.completions.create.side_effect = [resp_turn_1, resp_turn_2]

    model = GroqModel(groq=mock_groq, tools=[tool1, tool2])

    # ACT: Call process_text with a sample input
    response = model.process_text("What time is it and what is 6*7?")

    # ASSERT: Verify that the final response is as expected
    tool1.execute.assert_called_once()
    tool2.execute.assert_called_once_with(query="6 * 7")
    assert (
        response == "The time is 12:00 and 6*7 is 42."
    ), "The model should return the synthesised response after executing both tools."


def test_groq_model_executes_sequential_tool_chain():
    """Verify GroqModel chains tool executions across multiple conversation turns."""
    # ARRANGE: Create a mock Groq client that returns tool calls in sequence
    mock_groq = MagicMock(spec=Groq)

    search_tool = MagicMock()
    search_tool.name = "duckduckgo_search"
    search_tool.execute.return_value = "Title: Docs\nURL: https://example.com/docs"

    reader_tool = MagicMock()
    reader_tool.name = "url_reader"
    reader_tool.execute.return_value = "# Docs\nRelease date is 2026."

    # Turn 1: Model searches web
    call1 = _create_mock_tool_call(
        "call_search", "duckduckgo_search", {"query": "python release"}
    )
    resp_1 = MagicMock()
    resp_1.choices = [MagicMock(message=_create_mock_message(None, [call1]))]

    # Turn 2: Model reads the URL found in search results
    call2 = _create_mock_tool_call(
        "call_reader", "url_reader", {"url": "https://example.com/docs"}
    )
    resp_2 = MagicMock()
    resp_2.choices = [MagicMock(message=_create_mock_message(None, [call2]))]

    # Turn 3: Model returns final answer
    resp_3 = MagicMock()
    resp_3.choices = [
        MagicMock(message=_create_mock_message("The release date is 2026.", None))
    ]

    mock_groq.chat.completions.create.side_effect = [resp_1, resp_2, resp_3]

    model = GroqModel(groq=mock_groq, tools=[search_tool, reader_tool])

    # ACT: Call process_text with a sample input
    response = model.process_text("When is the next Python release?")

    # ASSERT: Verify that the final response is as expected
    search_tool.execute.assert_called_once_with(query="python release")
    reader_tool.execute.assert_called_once_with(url="https://example.com/docs")
    assert (
        response == "The release date is 2026."
    ), "The model should return the final answer after executing the tool chain."


def test_groq_model_enforces_max_orchestration_loop_guard():
    """Verify GroqModel breaks out gracefully if a runaway tool loop exceeds the iteration cap."""
    # ARRANGE: Create a mock Groq client that returns a tool call that triggers itself
    mock_groq = MagicMock(spec=Groq)

    looping_tool = MagicMock()
    looping_tool.name = "clock"
    looping_tool.execute.return_value = "2026-08-21T12:00:00"

    # Continually request the tool without terminating
    call_infinite = _create_mock_tool_call("call_inf", "clock", {})
    infinite_response = MagicMock()
    infinite_response.choices = [
        MagicMock(message=_create_mock_message(None, [call_infinite]))
    ]

    mock_groq.chat.completions.create.return_value = infinite_response

    max_loops = 5
    model = GroqModel(
        groq=mock_groq, tools=[looping_tool], max_orchestration_loops=max_loops
    )

    # ACT: Call process_text with a sample input
    response = model.process_text("Start the loop.")

    # ASSERT: Should have called the API up to the max loop cap (5 times) and returned a
    # fallback message
    assert (
        mock_groq.chat.completions.create.call_count == max_loops
    ), "The model should call the API up to the max orchestration loop limit."
    assert (
        "loop limit" in response.lower()
    ), "The model should return a message indicating the loop limit was reached."


def test_groq_model_storage_defaults_session_id():
    """Verify initialising GroqModel with a conversation storage instance defaults session ID to None."""
    # ARRANGE: Create a mock Groq client and conversation storage
    mock_groq = MagicMock(spec=Groq)
    mock_storage = MagicMock(spec=ConversationStorage)

    # ACT: Create the model with mocks
    model = GroqModel(groq=mock_groq, conversation_storage=mock_storage)

    # ASSERT: Verify that the session ID defaults to None
    assert (
        model.session_id is None
    ), "The session ID should default to None to prevent ghost session issues."


def test_groq_model_storage_process_text_creates_session():
    """Verify GroqModel creates a session ID when processing text with conversation storage."""
    # ARRANGE: Create a mock Groq client and conversation storage
    mock_groq = MagicMock(spec=Groq)

    mock_message = MagicMock()
    mock_message.content = "Response from assistant"
    mock_message.tool_calls = None

    mock_groq.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=mock_message)]
    )

    mock_storage = MagicMock(spec=ConversationStorage)

    model = GroqModel(groq=mock_groq, conversation_storage=mock_storage)

    # ACT: Call process_text with a sample input
    result = model.process_text("Hello, world!")

    # ASSERT: Verify that a session ID was created and the correct methods called on the conversation storage
    assert result == "Response from assistant"
    assert model.session_id is not None
    mock_storage.create_session.assert_called_once_with(session_id=model.session_id)

    expected_calls = [
        call(
            session_id=model.session_id,
            role="user",
            content="Hello, world!",
            tool_calls=None,
        ),
        call(
            session_id=model.session_id,
            role="assistant",
            content="Response from assistant",
            tool_calls=None,
        ),
    ]
    mock_storage.save_message.assert_has_calls(expected_calls)


def test_groq_model_storage_loading_session():
    """Verify GroqModel loads an existing session ID from conversation storage into the messages list."""
    # ARRANGE: Create a mock Groq client and conversation storage
    mock_groq = MagicMock(spec=Groq)
    mock_storage = MagicMock(spec=ConversationStorage)
    existing_session_id = "existing-session-id"

    mock_storage.get_session_messages.return_value = [
        {"role": "user", "content": "Initial prompt"},
        {"role": "assistant", "content": "Initial response"},
    ]

    model = GroqModel(
        groq=mock_groq,
        system_prompt="You are a helpful assistant.",
        conversation_storage=mock_storage,
    )

    # ACT: Load the existing session and then process text
    model.load_session(existing_session_id)
    result = model.process_text("Hello again!")

    # ASSERT: Verify that the existing session ID was loaded and used
    assert (
        model.session_id == existing_session_id
    ), "The session ID should match the existing session ID."
    assert model.messages[0] == {
        "role": "system",
        "content": "You are a helpful assistant.",
    }, "The first message should be the system prompt."
    assert model.messages[1] == {
        "role": "user",
        "content": "Initial prompt",
    }, "The second message should be the initial user prompt."
    assert model.messages[2] == {
        "role": "assistant",
        "content": "Initial response",
    }, "The third message should be the initial assistant response."


def test_groq_model_start_new_session_resets_session_id_and_messages():
    """Verify GroqModel's start_new_session method resets the session ID and clears the messages list."""
    # ARRANGE: Create a mock Groq client and conversation storage
    mock_groq = MagicMock(spec=Groq)
    mock_storage = MagicMock(spec=ConversationStorage)

    model = GroqModel(
        groq=mock_groq,
        system_prompt="You are a helpful assistant.",
        conversation_storage=mock_storage,
    )

    # Simulate an existing session
    model.session_id = "existing-session-id"
    model.messages = [{"role": "user", "content": "Some previous message"}]

    # ACT: Start a new session
    model.start_new_session()

    # ASSERT: Verify that the session ID is reset and messages list is cleared except for the system prompt
    assert model.session_id is None, "The session ID should be reset to None."
    assert model.messages == [
        {"role": "system", "content": "You are a helpful assistant."}
    ], "The messages list should only contain the system prompt."


def test_model_logs_warning_on_loop_limit(caplog):
    """Verify that the model logs a warning when the loop limit is reached."""
    # ARRANGE: Create a mock Groq client and conversation storage
    mock_groq = MagicMock(spec=Groq)
    mock_storage = MagicMock(spec=ConversationStorage)

    model = GroqModel(
        groq=mock_groq,
        system_prompt="You are a helpful assistant.",
        conversation_storage=mock_storage,
        max_orchestration_loops=1,  # Set a low loop limit for testing
    )

    # Simulate a scenario that would trigger the loop limit
    model.messages = [{"role": "user", "content": "Message that triggers loop"}]

    # ACT: Process text to trigger the loop limit
    with caplog.at_level("WARNING"):
        model.process_text("Trigger loop")

    # ASSERT: Verify that a warning was logged
    assert any(
        "loop_limit_reached" in record.message for record in caplog.records
    ), "A warning should be logged when the loop limit is reached."


def test_model_logs_info_on_model_used_for_query(caplog):
    """Verify that the model logs an info message when it is used for a query."""
    # ARRANGE: Create a mock Groq client and conversation storage
    mock_groq = MagicMock(spec=Groq)
    mock_storage = MagicMock(spec=ConversationStorage)

    model = GroqModel(
        groq=mock_groq,
        system_prompt="You are a helpful assistant.",
        conversation_storage=mock_storage,
    )

    model.messages = [{"role": "user", "content": "Message for the model"}]

    # ACT: Process text to trigger the model usage
    with caplog.at_level("INFO"):
        model.process_text("Trigger model usage")

    # ASSERT: Verify that an info message was logged
    assert any(
        "model_request_started" in record.message for record in caplog.records
    ), "An info message should be logged when the model is used for a query."


def test_model_logs_info_on_tool_execution_for_query(caplog):
    """Verify that the model logs an info message when a tool is executed for a query."""
    # ARRANGE: Create a mock Groq client, conversation storage, and tool
    mock_groq = MagicMock(spec=Groq)
    mock_storage = MagicMock(spec=ConversationStorage)
    mock_tool = MagicMock(spec=Tool)
    mock_tool.name = "mock_tool"

    model = GroqModel(
        groq=mock_groq,
        system_prompt="You are a helpful assistant.",
        conversation_storage=mock_storage,
        tools=[mock_tool],
    )

    tool_call = MagicMock()
    tool_call.id = "call_mock_1"
    tool_call.function.name = "mock_tool"
    tool_call.function.arguments = "{}"

    tool_call_response = MagicMock(
        choices=[MagicMock(message=MagicMock(content=None, tool_calls=[tool_call]))]
    )
    final_response = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Final answer", tool_calls=None))]
    )

    mock_groq.chat.completions.create.side_effect = [tool_call_response, final_response]

    # ACT: Process text to trigger the tool execution
    with caplog.at_level("INFO"):
        model.process_text("Trigger tool execution")

    # ASSERT: Verify that an info message was logged for the tool execution
    assert any(
        "executing_tool" in record.message for record in caplog.records
    ), "An info message should be logged when a tool is executed for a query."


def test_model_logs_info_on_loading_session(caplog):
    """Verify that the model logs an info message when a session is loaded."""
    # ARRANGE: Create a mock Groq client and conversation storage
    mock_groq = MagicMock(spec=Groq)
    mock_storage = MagicMock(spec=ConversationStorage)

    model = GroqModel(
        groq=mock_groq,
        system_prompt="You are a helpful assistant.",
        conversation_storage=mock_storage,
    )

    # ACT: Load a session to trigger the logging
    with caplog.at_level("INFO"):
        model.load_session("mock_session_id")

    # ASSERT: Verify that an info message was logged for loading the session
    assert any(
        "loading_session" in record.message for record in caplog.records
    ), "An info message should be logged when a session is loaded."


def test_model_logs_error_on_tool_execution_exception(caplog):
    """Verify that the model logs an error message when a tool execution raises an exception."""
    # ARRANGE: Create a mock Groq client, conversation storage, and tool
    mock_groq = MagicMock(spec=Groq)
    mock_storage = MagicMock(spec=ConversationStorage)
    mock_tool = MagicMock(spec=Tool)
    mock_tool.name = "mock_tool"

    model = GroqModel(
        groq=mock_groq,
        system_prompt="You are a helpful assistant.",
        conversation_storage=mock_storage,
        tools=[mock_tool],
    )

    tool_call = MagicMock()
    tool_call.id = "call_mock_1"
    tool_call.function.name = "mock_tool"
    tool_call.function.arguments = "{}"

    mock_tool.execute.side_effect = RuntimeError("Tool execution failed")

    tool_call_response = MagicMock(
        choices=[MagicMock(message=MagicMock(content=None, tool_calls=[tool_call]))]
    )
    final_response = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Final answer", tool_calls=None))]
    )

    mock_groq.chat.completions.create.side_effect = [tool_call_response, final_response]

    # ACT: Process text to trigger the tool execution exception
    with caplog.at_level("ERROR"):
        try:
            model.process_text("Trigger tool execution exception")
        except RuntimeError:
            pass

    # ASSERT: Verify that an error message was logged for the tool execution exception
    assert any(
        "error_executing_tool" in record.message for record in caplog.records
    ), "An error message should be logged when a tool execution raises an exception."


def test_model_logs_error_on_api_failure(caplog):
    """Verify that the model logs an error message when the API call fails."""
    # ARRANGE: Create a mock Groq client and conversation storage
    mock_groq = MagicMock(spec=Groq)
    mock_storage = MagicMock(spec=ConversationStorage)

    model = GroqModel(
        groq=mock_groq,
        system_prompt="You are a helpful assistant.",
        conversation_storage=mock_storage,
    )

    # Simulate an API failure
    mock_groq.chat.completions.create.side_effect = RuntimeError("API failure")

    # ACT: Process text to trigger the API failure
    with caplog.at_level("ERROR"):
        try:
            model.process_text("Trigger API failure")
        except RuntimeError:
            pass

    # ASSERT: Verify that an error message was logged for the API failure
    assert any(
        "model_api_error" in record.message for record in caplog.records
    ), "An error message should be logged when the API call fails."


def test_model_logs_error_on_missing_tool(caplog):
    """Verify that the model logs an error message when a tool is missing."""
    # ARRANGE: Create a mock Groq client and conversation storage
    mock_groq = MagicMock(spec=Groq)
    mock_storage = MagicMock(spec=ConversationStorage)

    model = GroqModel(
        groq=mock_groq,
        system_prompt="You are a helpful assistant.",
        conversation_storage=mock_storage,
        tools=[],  # No tools registered
    )

    tool_call = MagicMock()
    tool_call.id = "call_mock_1"
    tool_call.function.name = "missing_tool"
    tool_call.function.arguments = "{}"

    tool_call_response = MagicMock(
        choices=[MagicMock(message=MagicMock(content=None, tool_calls=[tool_call]))]
    )

    mock_groq.chat.completions.create.side_effect = [tool_call_response]

    # ACT: Process text to trigger the missing tool error
    with caplog.at_level("ERROR"):
        try:
            model.process_text("Trigger missing tool error")
        except RuntimeError:
            pass

    # ASSERT: Verify that an error message was logged for the missing tool
    assert any(
        "tool_not_registered" in record.message for record in caplog.records
    ), "An error message should be logged when a tool is missing."
