"""Ensure the presenter module handles the interaction between the model and view correctly."""

from unittest.mock import MagicMock
from src.presenter import Presenter, Model, View
import pytest


def test_presenter_attaches_callback_and_handles_user_submit():
    """Test that the presenter correctly attaches a callback and handles user submission."""
    # ARRANGE: Create mock instances of the model and view
    mock_model = MagicMock(spec=Model)
    mock_view = MagicMock(spec=View)

    mock_model.process_text.return_value = "Processed text"

    # ACT: Create a presenter instance with the mock model and view
    # and simulate a user submitting text through the view
    presenter = Presenter(model=mock_model, view=mock_view)

    mock_view.on_submit("Hello, World!")

    # ASSERT: Verify presenter sets up the view's callback correctly
    assert (
        mock_view.on_submit is not None
    ), "Presenter should attach a callback to the view's on_submit method."

    mock_model.process_text.assert_called_once_with("Hello, World!")
    mock_view.display_text.assert_called_once_with("Processed text")


def test_presenter_shows_and_hides_loading_indicator():
    """Test that the presenter correctly shows and hides a loading indicator when handling user input."""
    # ARRANGE: Create mock instances of the model and view
    mock_model = MagicMock(spec=Model)
    mock_view = MagicMock(spec=View)

    mock_model.process_text.return_value = "Processed text"

    # ACT: Create a presenter instance with the mock model and view
    # and simulate a user submitting text through the view
    presenter = Presenter(model=mock_model, view=mock_view)

    mock_view.on_submit("Hello, World!")

    # ASSERT: Verify that the loading indicator is shown and hidden correctly
    # Should be show loading -> process text -> hide loading -> display text
    assert mock_view.mock_calls == [
        ("show_loading", (), {}),
        ("hide_loading", (), {}),
        ("display_text", ("Processed text",), {}),
    ]


def test_presenter_handles_errors_gracefully():
    """Test that the presenter handles errors gracefully when processing text."""
    # ARRANGE: Create mock instances of the model and view
    mock_model = MagicMock(spec=Model)
    mock_view = MagicMock(spec=View)

    # Simulate an error in the model's process_text method
    mock_model.process_text.side_effect = Exception("Processing error")

    # ACT: Create a presenter instance with the mock model and view
    presenter = Presenter(model=mock_model, view=mock_view)

    # Simulate a user submitting text through the view
    mock_view.on_submit("Hello, World!")

    # ASSERT: Verify that the loading indicator is shown and hidden correctly
    assert mock_view.mock_calls == [
        ("show_loading", (), {}),
        ("hide_loading", (), {}),
        ("display_error", ("Error: Processing error",), {}),
    ]


def test_presenter_rejects_empty_or_whitespace_input():
    """Test that the presenter rejects empty or whitespace-only input."""
    # ARRANGE: Create mock instances of the model and view
    mock_model = MagicMock(spec=Model)
    mock_view = MagicMock(spec=View)

    # ACT: Create a presenter instance with the mock model and view
    presenter = Presenter(model=mock_model, view=mock_view)

    # Simulate a user submitting empty or whitespace-only text through the view
    mock_view.on_submit("   ")

    # ASSERT: Verify that the presenter returns early and does not call
    # further methods on the model or view
    mock_view.show_loading.assert_not_called()
    mock_view.hide_loading.assert_not_called()
    mock_view.display_text.assert_not_called()
    mock_view.display_error.assert_not_called()
    mock_model.process_text.assert_not_called()
