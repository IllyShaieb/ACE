"""view.py: Contains the view interfaces and implementations for the ACE program."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class IACEView(Protocol):
    """Protocol for ACE Views.

    This Protocol defines the methods that any concrete view implementation must provide.
    It ensures that the Presenter can interact with any view type in a consistent manner,
    regardless of the underlying display technology (e.g., console, smart glasses, smart
    mirror, phone app).
    """

    def display_message(self, sender: str, message: str):
        """Displays a message from a specified sender.

        ### Args
            sender (str): The name of the entity sending the message (e.g., "ACE", "YOU").
            message (str): The content of the message to display.
        """

    def get_user_input(self, prompt: str) -> str:
        """Gets input from the user.

        ### Args
            prompt (str): The prompt message to display to the user before awaiting input.

        ### Returns
            str: The user's input as a string, typically stripped of leading/trailing
                    whitespace.
        """

    def show_error(self, message: str):
        """Displays an error message to the user.

        ### Args
            message (str): The error message to display.
        """

    def show_info(self, message: str):
        """Displays an informational message to the user.

        ### Args
            message (str): The informational message to display.
        """


class ConsoleView(IACEView):
    """A concrete implementation of IACEView for console-based interaction.

    This view handles input and output directly through the command line
    interface (CLI). It implicitly adheres to the IACEView Protocol by
    implementing all its defined methods.
    """

    def display_message(self, sender: str, message: str):
        """Displays a message to the console.

        ### Args
            sender (str): The name of the sender (e.g., "ACE", "YOU").
            message (str): The message content.
        """
        print(f"{sender}: {message}")

    def get_user_input(self, prompt: str) -> str:
        """Gets user input from the console.

        ### Args
            prompt (str): The prompt to display before input.

        ### Returns
            str: The user's input, with leading/trailing whitespace removed.
        """
        return input(prompt).strip()

    def show_error(self, message: str):
        """Displays an error message to the console.

        ### Args
            message (str): The error message.
        """
        print(f"[ERROR] {message}")

    def show_info(self, message: str):
        """Displays an informational message to the console.

        ### Args
            message (str): The informational message.
        """
        print(f"[INFO] {message}")
