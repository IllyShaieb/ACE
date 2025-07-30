"""view.py: Contains the view interfaces and implementations for the ACE program."""

from typing import List, Protocol, runtime_checkable
import tkinter as tk
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox


@runtime_checkable
class IACEView(Protocol):
    """Protocol for ACE Views.

    This Protocol defines the methods that any concrete view implementation must provide.
    It ensures that the Presenter can interact with any view type in a consistent manner,
    regardless of the underlying display technology (e.g., console, smart glasses, smart
    mirror, phone app).
    """

    def run(self):
        """Starts the view's main loop.

        For a console app, this might do nothing. For a GUI, this starts the
        event loop (e.g., `root.mainloop()`).
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

    def set_input_handler(self, handler):
        """Sets the callback to be called when user submits input.

        ### Args
            handler (callable): A function that takes the user's input as an argument.
        """

    def clear_chat_history(self):
        """Clears the chat history from the view."""

    def clear_input(self):
        """Clears the input field in the view."""


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

    def set_input_handler(self, handler):
        """Sets the input handler callback.

        This method is not applicable for console-based interaction, as input
        is handled synchronously.
        """
        pass

    def run(self):
        """Starts the console view.

        This method does nothing for console-based interaction, as input/output
        is handled synchronously.
        """
        pass

    def clear_chat_history(self):
        """Clears the chat history.

        TODO: Implement a method to clear the console chat history.
        """
        pass

    def clear_input(self):
        """Clears the input field.

        This method is not applicable for console-based interaction, as input
        is handled synchronously.
        """
        pass


class DesktopView(IACEView):
    """A concrete implementation of IACEView for desktop GUI interaction.

    This view creates a simple chat-style window. It is designed to be
    controlled by a Presenter, receiving display commands and reporting
    user input events.
    """

    SENDER_COLOURS = {
        "ACE": "yellow",
        "ERROR": "red",
        "INFO": "cyan",
        "YOU": "white",
    }

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("ACE")

        # Store the chat and message history
        self._message_history = []
        self._chat_history = []

        # User actions
        self.query_response = None

        # Create the widgets and layout
        self._create_widgets()
        self._setup_tags()

        self._input_handler = None

    def _setup_tags(self):
        """Sets up text tags for different sender colours in the chat textbox."""
        for _, colour in self.SENDER_COLOURS.items():
            tag_name = f"sender_{colour.lower()}"
            self.chat_text.tag_config(tag_name, foreground=colour)

    def run(self):
        """Starts the GUI event loop."""
        self.root.mainloop()

    def close(self):
        """Closes the GUI window."""
        self.root.destroy()

    def get_chat_history(self) -> List:
        """Returns the chat history as a list of strings."""
        return self._message_history

    def clear_chat_history(self):
        """Clears the chat history."""
        self._message_history.clear()
        self.chat_text.delete(1.0, tk.END)

    def reset_input(self):
        """Resets the input entry field."""
        if hasattr(self, "input_entry"):
            self.input_entry.delete(0, tk.END)
            self.input_entry.configure(state=tk.NORMAL)
            self.set_input_enabled(True)

    def display_message(self, sender: str, message: str):
        """Displays a message in the chat window.

        ### Args
            sender (str): The name of the sender
            message (str): The message content.

        #### Notes
        - Possible special formatting for the following senders:
            - "ACE": cyan
            - "YOU": white
            - "ERROR": red
            - "INFO": blue
        """
        colour = self.SENDER_COLOURS.get(sender.upper(), "white")
        tag_name = f"sender_{colour}"

        # Format the message and add it to the history
        formatted_message = self._format_message(sender, message)
        self._message_history.append(formatted_message.strip())

        # Insert the message into the textbox with the colored tag
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, formatted_message, tag_name)
        self.chat_text.see(tk.END)
        self.chat_text.configure(state=tk.DISABLED)

    def _format_message(self, sender, message):
        """Formats the message for display in the chat window.

        ### Args
            sender (str): The name of the sender.
            message (str): The message content.
        ### Returns
            str: The formatted message string.
        """
        if sender.upper() in ("ERROR", "INFO"):
            return f"[{sender}] {message}\n\n"
        return f"{sender}: {message}\n\n"

    def show_error(self, message: str):
        """Displays an error message pop-up and logs it in the chat.

        ### Args
            message (str): The error message to display.
        """
        CTkMessagebox(title="Error", message=message, icon="cancel")
        self.display_message("ERROR", message)

    def show_info(self, message: str):
        """Displays an informational message pop-up and logs it in the chat.

        ### Args
            message (str): The informational message to display.
        """
        self.display_message("INFO", message)

    def get_user_input(self, prompt: str) -> str:
        """Gets user input from the input entry field.

        ### Args
            prompt (str): The prompt to display before awaiting input.

        ### Returns
            str: The user's input, stripped of leading/trailing whitespace.
        """
        return self.input_entry.get().strip()

    def set_input_handler(self, handler):
        """Sets the callback to be called when user submits input.

        This is required to handle user input asynchronously, allowing the
        Presenter to process the input without blocking the GUI.
        """
        self._input_handler = handler

    def set_input_enabled(self, enabled: bool):
        """Enables or disables the user input field and send button."""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.input_entry.configure(state=state)
        self.send_button.configure(state=state)

    def _create_widgets(self):
        """Initialises the GUI components for the chat interface."""
        self.root.geometry("900x500")
        self.root.resizable(True, True)

        # Use grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Create all the GUI components
        self._create_chat_area(self.root, row=0, column=0, col_span=2)
        self._create_input_area(self.root, row=1, column=0, col_span=2)

    def _create_chat_area(self, parent, row=0, column=1, col_span=2):
        """Creates the chat display area.

        ### Args
            parent: The parent widget to place the chat area in.
            row (int): The row index for grid placement.
            column (int): The column index for grid placement.
            col_span (int): The number of columns to span.
        """
        self.chat_text = ctk.CTkTextbox(parent, wrap=tk.WORD)
        self.chat_text.grid(
            row=row,
            column=column,
            columnspan=col_span,
            padx=20,
            pady=20,
            sticky="nsew",
        )
        self.chat_text.configure(state=tk.DISABLED)

    def _create_input_area(self, parent, row=1, column=0, col_span=2):
        """Creates the input area for user messages.

        ### Args
            parent: The parent widget to place the input area in.
            row (int): The row index for grid placement.
            column (int): The column index for grid placement.
            col_span (int): The number of columns to span.
        """

        def focus_on_letter(event):
            if event.char.isalpha() and self.root.focus_get() != self.input_entry:
                self.input_entry.focus()

        self.root.bind("<Key>", focus_on_letter)

        # Configure a sub section for the input area
        self._input_area = ctk.CTkFrame(parent)
        self._input_area.grid(
            row=row,
            column=column,
            columnspan=col_span,
            padx=20,
            pady=(0, 20),
            sticky="ew",
        )
        self._input_area.grid_columnconfigure(0, weight=1)
        self._input_area.grid_columnconfigure(1, weight=0)

        self.input_entry = ctk.CTkEntry(self._input_area, placeholder_text="Ask ACE")
        self.input_entry.bind("<Return>", lambda _: self._send_message())
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(5, 10), pady=10)

        self.send_button = ctk.CTkButton(
            self._input_area, text="Send", command=self._send_message
        )
        self.send_button.grid(row=0, column=1, sticky="e", padx=(0, 5), pady=10)

    def _send_message(self):
        """Handles sending a message when the user clicks the send button or presses Enter."""
        message = self.get_user_input("Ask ACE: ")
        if message:
            self.display_message("YOU", message)
            self.input_entry.delete(0, tk.END)
            self.chat_text.see(tk.END)

            # Force the GUI to update so the user's message appears immediately
            self.root.update_idletasks()

            # Get the users response
            if hasattr(self, "_input_handler"):
                self.set_input_enabled(False)
                if self._input_handler:
                    # Call the input handler with the user's message
                    self._input_handler(message)

            # Focus back on the input entry
            self.input_entry.focus()
            self.set_input_enabled(True)
