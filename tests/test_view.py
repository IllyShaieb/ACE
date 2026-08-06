"""Ensure the view module correctly handles user interactions and displays information."""

from unittest.mock import MagicMock
from src.view import PyQt6View


def test_submit_user_input_via_button(qtbot):
    """Test that the view correctly captures user input and triggers the on_submit callback."""
    # ARRANGE: Create a mock callback function and pass it to a PyQt6View instance
    mock_callback = MagicMock()
    view = PyQt6View()
    qtbot.addWidget(view)
    view.on_submit = mock_callback

    # ACT: Simulate user input and submission
    user_input = "Hello, World!"
    view.input_box.setText(user_input)
    view.submit_button.click()

    # ASSERT: Verify that the on_submit callback was called with the correct user input
    mock_callback.assert_called_once_with(user_input)
    assert (
        view.input_box.toPlainText() == ""
    ), "Input box should be cleared after submission."
