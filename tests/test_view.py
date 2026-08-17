"""Ensure the view module correctly handles user interactions and displays information."""

from unittest.mock import MagicMock, patch

from PyQt6.QtCore import Qt

from src.view import PyQt6View, Theme


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


def test_submit_user_input_via_ctrl_return_twice(qtbot):
    """Test that Ctrl+Return works for consecutive submissions."""
    # ARRANGE: Create a mock callback function and pass it to a PyQt6View instance
    mock_callback = MagicMock()
    view = PyQt6View()
    qtbot.addWidget(view)
    view.on_submit = mock_callback
    view.input_box.setFocus()

    # ACT: Submit two messages with Ctrl+Return
    first_input = "First message"
    second_input = "Second message"

    view.input_box.setPlainText(first_input)
    qtbot.keyClick(
        view.input_box,
        Qt.Key.Key_Return,
        Qt.KeyboardModifier.ControlModifier,
    )

    view.input_box.setPlainText(second_input)
    qtbot.keyClick(
        view.input_box,
        Qt.Key.Key_Return,
        Qt.KeyboardModifier.ControlModifier,
    )

    # ASSERT: Verify both submissions are handled and input is cleared each time
    mock_callback.assert_any_call(first_input)
    assert view.input_box.toPlainText() == ""
    mock_callback.assert_any_call(second_input)
    assert view.input_box.toPlainText() == ""


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


def test_hide_loading_enables_controls_and_restores_button_text(qtbot):
    """Test that the view correctly hides the loading indicator by enabling controls and
    restoring the submit button text."""
    # ARRANGE: Create a PyQt6View instance and show loading first
    view = PyQt6View()
    qtbot.addWidget(view)
    view.show_loading()

    # ACT: Call the hide_loading method
    view.hide_loading()

    # ASSERT: Verify that the text input and submit button are enabled
    # and the submit button text is restored to "Submit"
    assert view.input_box.isEnabled(), "Input box should be enabled after loading."
    assert (
        view.submit_button.isEnabled()
    ), "Submit button should be enabled after loading."
    assert (
        view.submit_button.text() == "Submit"
    ), "Submit button text should be 'Submit' after loading."


def test_display_error_shows_error_message(qtbot):
    """Test that the view correctly displays an error message in the output area."""
    # ARRANGE: Create a PyQt6View instance
    view = PyQt6View()
    qtbot.addWidget(view)

    # ACT: Call the display_error method with an error message
    error_message = "[ERROR] An error occurred."
    view.display_error(error_message)

    # ASSERT: Verify that the output area contains the error message
    output_area_text = view.output_area.toPlainText()
    assert (
        error_message in output_area_text
    ), f"Output area should contain the error message: {error_message}"


def test_view_defaults_to_dark_theme(qtbot):
    """Test that the view defaults to a dark theme."""
    # ARRANGE: Create a PyQt6View instance
    view = PyQt6View()
    qtbot.addWidget(view)

    # ACT: Nothing to do here since we are just checking the default theme

    # ASSERT: Verify view._is_dark_mode is True and verify the view's styleSheet
    # contains dark palette properties.
    assert view._is_dark_mode, "View should default to dark mode."
    assert (
        "background-color: #1e1e1e;" in view.styleSheet()
    ), "View should have dark background color in styleSheet."


def test_view_can_switch_to_light_theme(qtbot):
    """Test that the view can switch to a light theme."""
    # ARRANGE: Create a PyQt6View instance with light theme
    view = PyQt6View(theme=Theme.LIGHT)
    qtbot.addWidget(view)

    # ACT: Nothing to do here since we are just checking the light theme

    # ASSERT: Verify view._is_dark_mode is False and verify the view's styleSheet
    # contains light palette properties.
    assert not view._is_dark_mode, "View should be in light mode."
    assert (
        "background-color: #f5f7fb;" in view.styleSheet()
    ), "View should have light background color in styleSheet."


def test_view_can_switch_theme_via_button(qtbot):
    """Test that the view can switch themes via the theme button."""
    # ARRANGE: Create a PyQt6View instance with light theme
    view = PyQt6View(theme=Theme.LIGHT)
    qtbot.addWidget(view)

    # ACT: Click the theme button to switch to dark mode
    qtbot.mouseClick(view.theme_button, Qt.MouseButton.LeftButton)

    # ASSERT: Verify view._is_dark_mode is True and verify the view's styleSheet
    # contains dark palette properties.
    assert (
        view._is_dark_mode
    ), "View should be in dark mode after clicking the theme button."
    assert (
        "background-color: #1e1e1e;" in view.styleSheet()
    ), "View should have dark background color in styleSheet after switching themes."


def test_view_can_switch_model_via_combobox(qtbot):
    """Test that the view can switch models via the model selection combo box."""
    # ARRANGE: Create a PyQt6View instance and set a mock callback for model change
    view = PyQt6View()
    qtbot.addWidget(view)

    mock_model_change_callback = MagicMock()
    view.on_model_change = mock_model_change_callback

    current_index = view.model_selection.currentIndex()

    # ACT: Change the model selection in the combo box.
    view.model_selection.setCurrentIndex(
        (current_index + 1) % view.model_selection.count()
    )  # Switch to the next model in the list

    # ASSERT: Verify that the on_model_change callback was called with the correct model name
    expected_model_name = (
        view.model_selection.currentData() or view.model_selection.currentText()
    )
    mock_model_change_callback.assert_called_once_with(expected_model_name)


def test_display_text_converts_markdown_and_appends_to_output(qtbot):
    """Test that display_text converts Markdown via the formatter before appending."""

    # ARRANGE: Create a PyQt6View instance and mock the markdown_to_html function
    view = PyQt6View()
    qtbot.addWidget(view)

    # ACT: Call display_text with some Markdown text
    raw_markdown = "Raw **Markdown**"

    with patch(
        "src.view.markdown_to_html", side_effect=lambda x: f"<p>{x}</p>"
    ) as mock_formatter:
        view.display_text(raw_markdown)

        # ASSERT: Verify that the formatter was called
        mock_formatter.assert_called_once_with(raw_markdown)
