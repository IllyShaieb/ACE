"""core.presenters: This module defines the presenter classes for the ACE application,
mediating between the model and view components."""

from core.protocols import ModelProtocol, Sender, ViewProtocol


class ConsolePresenter:
    """Presenter for the console-based view, mediating between the model and view."""

    def __init__(
        self, model: ModelProtocol, view: ViewProtocol, welcome_message: str = ""
    ):
        """Initialize the presenter with the given model and view.

        Args:
            model (ModelProtocol): The model component to interact with.
            view (ViewProtocol): The view component to update based on model changes.
            welcome_message (str): The welcome message to display when the presenter runs.
                Defaults to an empty string if not provided.
        """
        self.model = model
        self.view = view
        self.welcome_message = welcome_message

        # Connect view events to presenter methods
        self.view.events.on_user_input.connect(self.handle_user_input)

    def run(self) -> None:
        """Display the welcome message (if any) and start the view."""
        if self.welcome_message:
            self.view.display_message(Sender.INFO, self.welcome_message)

        self.view.start()

    def handle_user_input(self, user_input: str) -> None:
        """Process user input and update the view accordingly.

        Args:
            user_input (str): The input received from the user.
        """
        # Sanitise input by stripping whitespace and converting to lowercase
        # for command recognition
        cleaned_input = user_input.strip().lower()

        # Ignore empty input as it doesn't require any action
        if not cleaned_input:
            return

        # Check for exit command to stop the view and end the application
        if cleaned_input == "exit":
            self.view.stop()
            return

        # Process the user input through the model and get a response
        response = self.model.process_query(user_input)
        self.view.display_message(Sender.ACE, response)
