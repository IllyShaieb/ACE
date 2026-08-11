"""The view module defines the user interface components of the application."""

from enum import Enum
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Theme(Enum):
    """An enumeration representing the available themes for the application."""

    DARK = "dark"
    LIGHT = "light"


class PyQt6View(QWidget):
    """A view class built using PyQt6."""

    on_submit: Callable[[str], None] | None

    def __init__(
        self, styles_dir: Path | None = None, theme: Theme = Theme.DARK
    ) -> None:
        """Initialise the view with a PyQt6 widget.

        Args:
            styles_dir (Path): The directory containing the QSS style files.
            theme (Theme): The theme to apply to the view.
        """
        super().__init__()
        self.on_submit = None


        self.setWindowIcon(
            QIcon(str(Path(__file__).parent.parent / "assets" / "app-icon.svg"))
        )
        self.setWindowTitle("ACE")

        self._is_dark_mode = theme in [Theme.DARK]
        self.styles_dir = (
            styles_dir or Path(__file__).parent.parent / "assets" / "styles"
        )

        self.theme_button = QPushButton()
        self.theme_button.clicked.connect(self.toggle_theme)

        self._apply_theme()

        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Type your message here...")

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self._handle_submit)
        self.output_area = QTextBrowser()

        # Ctrl + Return shortcut for submission
        self.input_box.installEventFilter(self)

        layout = QVBoxLayout()

        layout.addWidget(self.theme_button, 0, Qt.AlignmentFlag.AlignRight)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input_box, 1)
        input_row.addWidget(self.submit_button)

        layout.addWidget(self.output_area, 4)
        layout.addLayout(input_row, 1)
        self.setLayout(layout)

        self.input_box.setFocus()

    def toggle_theme(self) -> None:
        """Toggle between dark and light themes."""
        self._is_dark_mode = not self._is_dark_mode
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Load and apply QSS stylesheet based on current _is_dark_mode state."""
        theme_name = "dark" if self._is_dark_mode else "light"
        qss_file = self.styles_dir / f"{theme_name}.qss"

        # Update button icon to show what clicking it will do (or current state)
        self.theme_button.setText("☀️" if self._is_dark_mode else "🌙")

        if qss_file.exists():
            with open(qss_file, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Warning: QSS file {qss_file} not found.")

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
        self.repaint()  # Force the UI to update immediately to show the loading state

    def hide_loading(self) -> None:
        """Hide the loading indicator by enabling the input box and restoring the submit button text."""
        self.input_box.setDisabled(False)
        self.submit_button.setDisabled(False)
        self.submit_button.setText("Submit")
        self.input_box.setFocus()
        self.repaint()  # Force the UI to update immediately to show the normal state

    def display_error(self, message: str) -> None:
        """Display an error message in the output area.

        Args:
            message (str): The error message to display.
        """
        self.output_area.append(f'<span style="color: red;">{message}</span>')

    def eventFilter(self, source, event):  # type: ignore
        """Event filter to handle Ctrl + Return key press in the input box.

        Args:
            source: The source of the event.
            event: The event object.

        Returns:
            bool: True if the event is handled, False otherwise.
        """
        if (
            source is self.input_box
            and event.type() == QEvent.Type.KeyPress
            and event.key() == Qt.Key.Key_Return
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self._handle_submit()
            return True
        return super().eventFilter(source, event)


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
