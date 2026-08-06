"""The presenter module handles the interaction between the model and view."""

from typing import Callable, Protocol


class Model(Protocol):
    """A model deals with the business logic of the application."""

    def process_text(self, text: str) -> str: ...


class View(Protocol):
    """A view is responsible for displaying information to the user and capturing user input."""

    on_submit: Callable[[str], None] | None

    def display_text(self, text: str) -> None: ...

    def show_loading(self) -> None: ...

    def hide_loading(self) -> None: ...

    def display_error(self, message: str) -> None: ...


class Presenter:
    """The Presenter class acts as an intermediary between the model and view."""

    def __init__(self, model: Model, view: View):
        """Initialise the presenter with a model and a view.

        Args:
            model (Model): The model instance to interact with.
            view (View): The view instance to interact with.
        """
        self.model = model
        self.view = view

        # Connect the view to the presenter
        self.view.on_submit = self.handle_submit

    def handle_submit(self, text: str) -> None:
        """Handle the event when the user submits text through the view.

        Args:
            text (str): The text submitted by the user.
        """
        # Return silently if no text is provided
        if not text.strip():
            return

        # Show a loading indicator while processing the text
        self.view.show_loading()

        try:
            # Process the text using the model
            result = self.model.process_text(text)

            # Hide the loading indicator after processing
            self.view.hide_loading()

        except Exception as e:
            # Handle any errors that occur during processing
            self.view.hide_loading()
            self.view.display_error(f"Error: {str(e)}")
            return

        # Display the processed text in the view
        self.view.display_text(result)
