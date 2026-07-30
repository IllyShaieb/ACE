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
