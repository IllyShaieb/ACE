"""The view module defines the user interface components of the application."""

from typing import Callable

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtWidgets import (
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTextBrowser,
)


class PyQt6View(QWidget):
    """A view class built using PyQt6."""

    on_submit: Callable[[str], None] | None

    def __init__(self):
        """Initialise the view with a PyQt6 widget."""
        super().__init__()
        self.on_submit = None
        self.input_box = QTextEdit()
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self._handle_submit)
        self.output_area = QTextBrowser()

        layout = QVBoxLayout()

        input_row = QHBoxLayout()
        input_row.addWidget(self.input_box, 1)
        input_row.addWidget(self.submit_button)

        layout.addWidget(self.output_area, 4)
        layout.addLayout(input_row, 1)
        self.setLayout(layout)

    def _handle_submit(self):
        if self.on_submit:
            self.on_submit(self.input_box.toPlainText())
        self.input_box.clear()

    def display_text(self, text: str) -> None:
        """Display the given text in the output area.

        Args:
            text (str): The text to display.
        """
        self.output_area.append(text)

    def show_loading(self) -> None:
        """Show a loading indicator by disabling the input box and changing the submit button text."""
        self.input_box.setDisabled(True)
        self.submit_button.setDisabled(True)
        self.submit_button.setText("...")

    def hide_loading(self) -> None:
        """Hide the loading indicator by enabling the input box and restoring the submit button text."""
        self.input_box.setDisabled(False)
        self.submit_button.setDisabled(False)
        self.submit_button.setText("Submit")

    def display_error(self, message: str) -> None:
        """Display an error message in the output area.

        Args:
            message (str): The error message to display.
        """
        self.output_area.append(f'<span style="color: red;">{message}</span>')


if __name__ == "__main__":
    app = QApplication([])
    view = PyQt6View()

    def _on_submit(text: str) -> None:
        """Handle the event when the user submits text through the view.

        Args:
            text (str): The text submitted by the user.
        """
        from time import sleep

        # Return silently if no text is provided
        if not text.strip():
            return

        # Display the user's message immediately.
        view.display_text(f"You: {text}")
        view.show_loading()

        sleep(1)  # Simulate processing delay

        # Display a mock response based on the input text
        if "error" in text.lower():
            view.display_error(
                "Error: Simulated error: something went wrong while processing your text."
            )
        else:
            view.display_text("ACE: This is a simple demo response.")

        view.hide_loading()

    view.on_submit = _on_submit
    view.show()
    app.exec()
