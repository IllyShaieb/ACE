"""The view module defines the user interface components of the application."""

from typing import Callable

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtWidgets import QTextEdit, QPushButton, QVBoxLayout


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

        layout = QVBoxLayout()
        layout.addWidget(self.input_box)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)

    def _handle_submit(self):
        if self.on_submit:
            self.on_submit(self.input_box.toPlainText())
        self.input_box.clear()

    def display_text(self, text: str) -> None: ...

    def show_loading(self) -> None: ...

    def hide_loading(self) -> None: ...

    def display_error(self, message: str) -> None: ...


if __name__ == "__main__":
    app = QApplication([])
    view = PyQt6View()
    view.on_submit = lambda text: print(f"Submitted: {text}")
    view.show()
    app.exec()
