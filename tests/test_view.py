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


def test_display_text_appends_to_output_area(qtbot):
    """Test that the view correctly displays text in the output area."""
    # ARRANGE: Create a PyQt6View instance
    view = PyQt6View()
    qtbot.addWidget(view)

    # ACT: Call the display_text method with some text
    messages = ["First message", "Second message"]
    for message in messages:
        view.display_text(message)

    # ASSERT: Verify that the output area contains the displayed text
    output_area_text = view.output_area.toPlainText()
    for message in messages:
        assert (
            message in output_area_text
        ), f"Output area should contain the message: {message}"


def test_show_loading_disables_controls_and_updates_button_text(qtbot):
    """Test that the view correctly shows a loading indicator by disabling controls and
    updating the submit button text."""
    # ARRANGE: Create a PyQt6View instance
    view = PyQt6View()
    qtbot.addWidget(view)

    # ACT: Call the show_loading method
    view.show_loading()

    # ASSERT: Verify that the text input and submit button are disabled
    # and the submit button text is changed to "..."
    assert (
        not view.input_box.isEnabled()
    ), "Input box should be disabled during loading."
    assert (
        not view.submit_button.isEnabled()
    ), "Submit button should be disabled during loading."
    assert (
        view.submit_button.text() == "..."
    ), "Submit button text should be '...' during loading."
