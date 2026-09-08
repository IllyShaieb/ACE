"""Ensure the presenter module handles the interaction between the model and view correctly."""

import logging
from unittest.mock import MagicMock

from src.presenter import Model, Presenter, View
from src.storage import ConversationStorage


def test_presenter_attaches_callback_and_handles_user_submit():
    """Test that the presenter correctly attaches a callback and handles user submission."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    mock_model.process_text.return_value = "Processed text"
    mock_storage.get_recent_sessions.return_value = ["session1"]

    # ACT: Create a presenter instance with the mock model and view
    # and simulate a user submitting text through the view
    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    mock_view.on_submit("Hello, World!")

    # ASSERT: Verify presenter sets up the view's callback correctly
    assert (
        mock_view.on_submit is not None
    ), "Presenter should attach a callback to the view's on_submit method."

    mock_model.process_text.assert_called_once_with("Hello, World!")
    mock_view.display_text.assert_any_call("## You:\n\nHello, World!\n\n")
    mock_view.display_text.assert_any_call("## ACE:\n\nProcessed text\n\n")
    mock_view.populate_sessions.assert_called_with(["session1"])


def test_presenter_shows_and_hides_loading_indicator():
    """Test that the presenter correctly shows and hides a loading indicator when handling user input."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    mock_model.process_text.return_value = "Processed text"

    # ACT: Create a presenter instance with the mock model and view
    # and simulate a user submitting text through the view
    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    mock_view.on_submit("Hello, World!")

    # ASSERT: Verify that the loading indicator is shown and hidden correctly
    # Should be display user text -> show loading -> process text -> hide loading -> display ACE text
    assert mock_view.mock_calls == [
        ("populate_sessions", (mock_storage.get_recent_sessions.return_value,), {}),
        ("display_text", ("## You:\n\nHello, World!\n\n",), {}),
        ("show_loading", (), {}),
        ("hide_loading", (), {}),
        ("display_text", ("## ACE:\n\nProcessed text\n\n",), {}),
        ("populate_sessions", (mock_storage.get_recent_sessions.return_value,), {}),
    ]


def test_presenter_handles_errors_gracefully():
    """Test that the presenter handles errors gracefully when processing text."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    # Simulate an error in the model's process_text method
    mock_model.process_text.side_effect = Exception("Processing error")

    # ACT: Create a presenter instance with the mock model, view, and storage
    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    # Simulate a user submitting text through the view
    mock_view.on_submit("Hello, World!")

    # ASSERT: Verify that the loading indicator is shown and hidden correctly
    assert mock_view.mock_calls == [
        ("populate_sessions", (mock_storage.get_recent_sessions.return_value,), {}),
        ("display_text", ("## You:\n\nHello, World!\n\n",), {}),
        ("show_loading", (), {}),
        ("hide_loading", (), {}),
        ("display_error", ("[ERROR] Processing error\n\n",), {}),
    ]


def test_presenter_rejects_empty_or_whitespace_input():
    """Test that the presenter rejects empty or whitespace-only input."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    # ACT: Create a presenter instance with the mock model, view, and storage
    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    # Simulate a user submitting empty or whitespace-only text through the view
    mock_view.on_submit("   ")

    # ASSERT: Verify that the presenter returns early and does not call
    # further methods on the model or view
    mock_view.show_loading.assert_not_called()
    mock_view.hide_loading.assert_not_called()
    mock_view.display_text.assert_not_called()
    mock_view.display_error.assert_not_called()
    mock_model.process_text.assert_not_called()


def test_presenter_handles_model_change():
    """Test that the presenter correctly handles model changes."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    # ACT: Create a presenter instance with the mock model and view
    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    # Simulate a user changing the model selection through the view
    new_model_name = "NewModel"
    mock_view.on_model_change(new_model_name)

    # ASSERT: Verify that the presenter's handle_model_change method updates the model's name
    assert (
        mock_model.model_name == new_model_name
    ), "Presenter should update the model's name on model change."


def test_presenter_populates_recent_sessions_on_initialisation():
    """Test that the presenter populates recent sessions on initialisation."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    mock_storage.get_recent_sessions.return_value = ["session1", "session2"]

    # ACT: Create a presenter instance with the mock model, view, and storage
    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    # ASSERT: Verify that the view is populated with recent sessions
    mock_view.populate_sessions.assert_called_once_with(["session1", "session2"])


def test_presenter_sets_current_session_on_selection():
    """Test that the presenter sets the current session when a session is selected."""
    # ARRANGE: Create mock instances of the model, view, storage, and presenter
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    mock_storage.get_session_messages.return_value = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hello! How can I help?"},
    ]

    # ACT: Simulate a user selecting a session through the view
    selected_session_id = "session1"
    mock_view.on_session_selected(selected_session_id)

    # ASSERT: Verify that the presenter's conversation storage loads the selected session
    mock_storage.get_session_messages.assert_called_once_with(selected_session_id)
    mock_view.clear_chat.assert_called_once()

    for message in mock_storage.get_session_messages.return_value:
        sender = "You" if message["role"] == "user" else "ACE"
        content = message["content"]
        mock_view.display_text.assert_any_call(f"## {sender}:\n\n{content}\n\n")


def test_presenter_handles_new_chat():
    """Test that the presenter handles starting a new chat correctly."""
    # ARRANGE: Create mock instances of the model, view, storage and presenter
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"
    mock_model.session_id = "previous_session_id"

    mock_model.start_new_session.side_effect = lambda: setattr(
        mock_model, "session_id", None
    )

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    # ACT: Start a new chat through the presenter
    mock_view.reset_mock()
    mock_storage.reset_mock()

    presenter.handle_new_chat()

    # ASSERT: Verify that the view clears the chat
    mock_view.clear_chat.assert_called_once()
    mock_view.display_text.assert_not_called()
    mock_storage.get_session_messages.assert_not_called()
    mock_view.populate_sessions.assert_not_called()
    assert (
        getattr(mock_model, "session_id", None) is None
    ), "Expected the model's session_id to be None after starting a new chat."


def test_presenter_logs_debug_on_initialisation(caplog):
    """Test that the presenter logs a debug message on initialisation."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    # ACT: Initialise the presenter
    with caplog.at_level(logging.DEBUG):
        Presenter(model=mock_model, view=mock_view, conversation_storage=mock_storage)

    # ASSERT: Verify that a debug message was logged
    assert any(
        "presenter_initialised" in message for message in caplog.messages
    ), "Expected a debug message indicating presenter initialisation."


def test_presenter_logs_info_on_switching_model(caplog):
    """Test that the presenter logs an info message when switching models."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    # ACT: Change the model through the presenter
    with caplog.at_level(logging.INFO):
        new_model_name = "new_model"
        mock_view.on_model_change(new_model_name)

    # ASSERT: Verify that an info message was logged
    assert any(
        "model_changed" in message for message in caplog.messages
    ), "Expected an info message indicating model change."


def test_presenter_logs_error_on_processing_exception(caplog):
    """Test that the presenter logs an error message when processing text raises an exception."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"
    mock_model.process_text.side_effect = Exception("Processing error")

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    # ACT: Submit text through the presenter
    with caplog.at_level(logging.ERROR):
        mock_view.on_submit("test message")

    # ASSERT: Verify that an error message was logged
    assert any(
        "processing_error" in message for message in caplog.messages
    ), "Expected an error message indicating processing failure."


def test_presenter_logs_info_on_session_selected(caplog):
    """Test that the presenter logs an info message when a session is selected."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)
    mock_storage.get_session_messages.return_value = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]

    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    session_id = "test_session"

    # ACT: Select a session through the presenter
    with caplog.at_level(logging.INFO):
        mock_view.on_session_selected(session_id)

    # ASSERT: Verify that an info message was logged
    assert any(
        "session_selected" in message for message in caplog.messages
    ), "Expected an info message indicating session selection."


def test_presenter_logs_debug_on_new_chat(caplog):
    """Test that the presenter logs a debug message when a new chat is started."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"
    mock_model.session_id = "previous_session"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    # ACT: Start a new chat through the presenter callback
    with caplog.at_level(logging.DEBUG):
        mock_view.on_new_chat()

    # ASSERT: Verify that a debug message was logged
    assert any(
        "new_chat_started" in message for message in caplog.messages
    ), "Expected a debug message indicating a new chat was started."


def test_presenter_logs_debug_on_empty_submission(caplog):
    """Test that the presenter logs a debug message when an empty submission is made."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)

    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    # ACT: Submit an empty message through the presenter callback
    with caplog.at_level(logging.DEBUG):
        mock_view.on_submit("")

    # ASSERT: Verify that a debug message was logged
    assert any(
        "discarding_empty_input" in message for message in caplog.messages
    ), "Expected a debug message indicating that empty input was discarded."


def test_presenter_handles_session_selection_exception(caplog):
    """Test that the presenter handles an exception during session selection gracefully."""
    # ARRANGE: Create mock instances of the model, view, and storage
    mock_model = MagicMock(spec=Model)
    mock_model.model_name = "test_model"

    mock_view = MagicMock(spec=View)
    mock_storage = MagicMock(spec=ConversationStorage)
    mock_storage.get_session_messages.side_effect = Exception("Test exception")

    presenter = Presenter(
        model=mock_model, view=mock_view, conversation_storage=mock_storage
    )

    session_id = "test_session"

    # ACT: Select a session through the presenter
    with caplog.at_level(logging.ERROR):
        mock_view.on_session_selected(session_id)

    # ASSERT: Verify that the view displayed an error message, and an error was logged
    mock_view.display_error.assert_called_once_with("[ERROR] Test exception\n\n")
    assert any(
        "processing_error" in message for message in caplog.messages
    ), "Expected an error message indicating a processing error during session selection."
