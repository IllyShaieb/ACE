"""view.py: Contains the view interfaces and implementations for the ACE program."""

import sys
import tkinter as tk
from datetime import datetime
from typing import Any, Callable, List, Optional, Protocol, runtime_checkable

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from typing_extensions import Literal

JustifyMethod = Literal["left", "right", "center"]


@runtime_checkable
class IACEView(Protocol):
    """Protocol for ACE Views.

    This Protocol defines the methods that any concrete view implementation must provide.
    It ensures that the Presenter can interact with any view type in a consistent manner,
    regardless of the underlying display technology (e.g., console, smart glasses, smart
    mirror, phone app).
    """

    chat_history = []

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

    def get_user_input(self, prompt: str) -> str:  # type: ignore
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

    def set_input_handler(self, handler: Callable):
        """Sets the callback to be called when user submits input.

        ### Args
            handler (callable): A function that takes the user's input as an argument.
        """

    def clear_chat_history(self):
        """Clears the chat history from the view."""

    def clear_input(self):
        """Clears the input field in the view."""

    def close(self):
        """Closes the view.

        This method should clean up any resources used by the view, such as closing
        GUI windows or terminating event loops.
        """

    def show_typing_indicator(self):
        """Informs the user that ACE is responding."""

    def hide_typing_indicator(self):
        """Hides the visual indicator for processing."""

    def display_conversations(
        self,
        conversations: list,
        select_handler: Optional[Callable] = None,
        delete_handler: Optional[Callable] = None,
        new_chat_handler: Optional[Callable] = None,
    ):
        """Displays the list of conversations to the user.

        ### Args
            conversations (list): The list of conversations to display.
            select_handler (Optional[Callable]): A callback function to handle conversation selection.
            delete_handler (Optional[Callable]): A callback function to handle conversation deletion.
            new_chat_handler (Optional[Callable]): A callback function to handle starting a new chat.
        """

    def show_confirmation(self, title: str, message: str) -> bool:  # type: ignore
        """Displays a confirmation dialog to the user.

        ### Args
            title (str): The title of the confirmation dialog.
            message (str): The message to display in the dialog.

        ### Returns
            bool: True if the user confirmed, False otherwise.
        """

    def after(self, delay: int, callback: Callable):
        """Schedules a callback to be called after a delay.

        ### Args
            delay (int): The delay in milliseconds before calling the callback.
            callback (Callable): The function to call after the delay.
        """

    def track_action(
        self, action_func: Callable, description: str = "ACE is thinking..."
    ) -> Any:
        """Tracks the execution of a function with a progress spinner.

        ### Args
            action_func (Callable): The function to execute.
            description (str): The text to display next to the spinner.

        ### Returns
            Any: The return value of the action_func.
        """

    def scroll_to_bottom(self):
        """Forces the chat view to scroll to the latest message."""


class ConsoleView(IACEView):
    """A concrete implementation of IACEView for console-based interaction.

    This view handles input and output directly through the command line
    interface (CLI). It implicitly adheres to the IACEView Protocol by
    implementing all its defined methods.
    """

    SENDER_COLOURS = {
        "ACE": ("cyan", "cyan"),  # (border_colour, text_colour)
        "ERROR": ("red", "red"),
        "INFO": ("white", "white"),
        "YOU": ("magenta", "magenta"),
    }

    def __init__(self):
        self.console = Console()

    def display_message(self, sender: str, message: str):
        """Displays a message to the console and adds it to the chat history.

        ### Args
            sender (str): The name of the sender (e.g., "ACE", "YOU").
            message (str): The message content.
        """
        border_colour, text_colour = self.SENDER_COLOURS.get(
            sender.upper(), ("white", "white")
        )

        sender_upper = sender.upper()

        justify: JustifyMethod
        match sender_upper:
            case "ACE":
                justify = "left"
            case "YOU":
                justify = "right"
            case _:
                justify = "center"

        # Don't use panel for INFO
        if sender_upper == "INFO":
            self.console.print(
                f"[{border_colour}]INFO: {message}[/{border_colour}]", justify=justify
            )
        else:
            panel = Panel(
                Text(message, style=text_colour, justify=justify),
                title=sender,
                border_style=border_colour,
                expand=False,
            )
            self.console.print(panel, justify=justify, markup=True)

        self.chat_history.append(f"{sender}: {message}")

    def get_user_input(self, prompt: str) -> str:
        """Gets user input from the console.

        ### Args
            prompt (str): The prompt to display before input.

        ### Returns
            str: The user's input, with leading/trailing whitespace removed.
        """
        _, text_colour = self.SENDER_COLOURS["YOU"]

        user_input = self.console.input(
            f"[bold {text_colour}]{prompt}[/bold {text_colour}]"
        ).strip()
        self.chat_history.append(f"YOU: {user_input}")

        return user_input

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
        self.console.clear()

    def clear_input(self):
        """Clears the last line from the console after input is submitted.

        This uses ANSI escape codes to move the cursor up one line and clear it,
        preventing the raw input from remaining on screen before the formatted
        chat bubble is displayed.
        """
        # \x1b[1A: Move cursor up one line
        # \x1b[2K: Clear entire line
        sys.stdout.write("\x1b[1A\x1b[2K")
        sys.stdout.flush()

    def close(self):
        """Closes the console view.

        This method does nothing for console-based interaction, as there is no
        GUI to close.
        """
        pass

    def show_typing_indicator(self):
        """Informs the user that ACE is responding.

        This is handled by the `track_action` method for synchronous console operations.
        """
        pass

    def hide_typing_indicator(self):
        """Hides the visual indicator for processing.

        This is handled by the `track_action` method for synchronous console operations.
        """
        pass

    def display_conversations(
        self,
        conversations: List,
        select_handler=None,
        delete_handler=None,
        new_chat_handler=None,
    ):
        """Displays the list of conversations to the user.

        TODO: Implement the display logic for conversations.

        ### Args
            conversations (list): The list of conversations to display.
            select_handler (Optional[Callable]): A callback function to handle conversation selection.
            delete_handler (Optional[Callable]): A callback function to handle conversation deletion.
            new_chat_handler (Optional[Callable]): A callback function to handle starting a new chat.
        """
        pass

    def show_confirmation(self, title: str, message: str) -> bool:
        """Displays a confirmation dialog to the user.

        TODO: Implement the confirmation dialog logic for the console.

        ### Args
            title (str): The title of the confirmation dialog.
            message (str): The message to display in the dialog.

        ### Returns
            bool: True if the user confirmed, False otherwise.
        """
        return False

    def after(self, delay: int, callback: Callable):
        """Schedules a callback to be called after a delay.

        TODO: Implement the scheduling logic for the console.

        ### Args
            delay (int): The delay in milliseconds before calling the callback.
            callback (Callable): The function to call after the delay.
        """
        pass

    def track_action(
        self, action_func: Callable, description: str = "ACE is thinking..."
    ) -> Any:
        """Tracks the execution of a function with a progress spinner.

        ### Args
            action_func (Callable): The function to execute.
            description (str): The text to display next to the spinner.

        ### Returns
            Any: The return value of the action_func.
        """
        with Progress(
            SpinnerColumn("dots", style=f"bold {self.SENDER_COLOURS['ACE'][0]}"),
            TextColumn(f"[{self.SENDER_COLOURS['ACE'][0]}]{description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(description, total=None)
            return action_func()

    def scroll_to_bottom(self):
        """Forces the chat view to scroll to the latest message.

        This method does nothing for console-based interaction.
        """
        pass


class DesktopView(IACEView):
    """
    A re-architected implementation of IACEView for a responsive and stable
    desktop GUI. It uses a CTkTextbox for the chat display to ensure reliable
    scrolling and high performance.
    """

    # Material 3 Dark Theme Color Palette
    PALETTE = {
        "primary": "#A7E8F1",
        "on_primary": "#0E4F58",
        "primary_container": "#157784",
        "on_primary_container": "#D3F4F8",
        "secondary": "#BDD7DB",
        "on_secondary": "#243E42",
        "secondary_container": "#365D63",
        "on_secondary_container": "#DEEBED",
        "tertiary": "#BEBADE",
        "on_tertiary": "#252145",
        "tertiary_container": "#373168",
        "on_tertiary_container": "#DEDCEF",
        "background": "#1F1F1F",
        "on_background": "#E6E6E6",
        "surface": "#1F1F1F",
        "on_surface": "#E6E6E6",
        "surface_variant": "#475152",
        "on_surface_variant": "#929FA0",
        "outline": "#929FA0",
        "error": "#FF9999",
        "on_error": "#660000",
        "error_container": "#4D0000",
        "on_error_container": "#FFCCCC",
    }

    SENDER_COLOURS = {
        "ACE": PALETTE["primary"],
        "ERROR": PALETTE["error"],
        "INFO": PALETTE["on_surface_variant"],
        "YOU": PALETTE["tertiary"],
    }

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("ACE")
        self.root.geometry("900x600")
        self.root.minsize(500, 400)
        self.root.configure(fg_color=self.PALETTE["background"])

        # User actions
        self._input_handler = None
        self._typing_animation_running = False

        # Create the widgets and layout
        self._create_widgets()
        self._configure_tags()

        self.chat_history = []  # Initialize chat history for DesktopView

    def run(self):
        """Starts the GUI event loop."""
        self.root.mainloop()

    def close(self):
        """Closes the GUI window."""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def set_input_handler(self, handler: Callable):
        """Sets the callback for user input."""
        self._input_handler = handler

    def get_user_input(self, prompt: Optional[str] = None) -> str:
        """Gets user input from the input entry field."""
        user_input = self.input_entry.get().strip()
        self.chat_history.append(f"YOU: {user_input}")

        return user_input

    def clear_chat_history(self):
        """Clears the chat history from the textbox."""
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.configure(state="disabled")

        self.chat_history = []  # Clear the chat history list

    def clear_input(self):
        """Clears the input entry field."""
        self.input_entry.delete(0, tk.END)

    def display_message(self, sender: str, message: str):
        """Displays a message in the chat window."""
        self.chat_display.configure(state="normal")

        sender_tag = sender.upper()

        match sender_tag:
            case "ERROR" | "INFO":
                formatted_line = f"[{sender}] {message}\n\n"
            case _:
                formatted_line = f"{sender}: {message}\n\n"

        # Insert the formatted line with the appropriate tag for color and justification
        self.chat_display.insert(tk.END, formatted_line, (sender_tag,))
        self.chat_history.append(formatted_line.strip())

        self.chat_display.configure(state="disabled")
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """Forces the chat view to scroll to the latest message."""
        self.chat_display.see(tk.END)

    def show_error(self, message: str):
        """Displays an error message."""
        self.display_message("ERROR", message)
        CTkMessagebox(
            title="Error",
            message=message,
            icon="cancel",
            button_color=self.PALETTE["error_container"],
            button_text_color=self.PALETTE["on_error_container"],
        )

    def show_info(self, message: str):
        """Displays an informational message."""
        self.display_message("INFO", message)

    def show_typing_indicator(self):
        """Displays a visual indicator that the application is processing."""
        self.set_input_enabled(False)
        self.send_button.configure(text="...")

        self._typing_indicator_label.grid()  # Show the label

        if not self._typing_animation_running:
            self._typing_animation_running = True
            self._animate_typing_indicator()

    def hide_typing_indicator(self):
        """Hides the visual indicator for processing."""
        self._typing_animation_running = False
        self._typing_indicator_label.grid_remove()  # Hide the label
        self.set_input_enabled(True)
        self.send_button.configure(text="Send")

    def display_conversations(
        self,
        conversations: list,
        select_handler: Optional[Callable] = None,
        delete_handler: Optional[Callable] = None,
        new_chat_handler: Optional[Callable] = None,
    ):
        """Displays a list of past conversations in the sidebar."""
        for widget in self._history_frame.winfo_children():
            widget.destroy()

        if new_chat_handler:
            ctk.CTkButton(
                self._history_frame,
                text="+ New Chat",
                command=new_chat_handler,
                fg_color=self.PALETTE["primary_container"],
                text_color=self.PALETTE["on_primary_container"],
                hover_color=self.PALETTE["primary"],
            ).pack(fill="x", padx=5, pady=(5, 10))

        for conversation_id, timestamp in conversations:
            item_frame = ctk.CTkFrame(self._history_frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=5, pady=2)
            item_frame.grid_columnconfigure(0, weight=1)

            dt = datetime.fromisoformat(timestamp)
            display_text = f"ID: {conversation_id}\n{dt.strftime('%Y-%m-%d %H:%M')}"

            select_cmd = (
                (lambda cid=conversation_id: select_handler(cid))
                if select_handler
                else None
            )
            ctk.CTkButton(
                item_frame,
                text=display_text,
                command=select_cmd,
                anchor="w",
                fg_color=self.PALETTE["secondary_container"],
                text_color=self.PALETTE["on_secondary_container"],
                hover_color=self.PALETTE["secondary"],
            ).grid(row=0, column=0, sticky="ew")

            if delete_handler:
                delete_cmd = (
                    (lambda cid=conversation_id: delete_handler(cid))
                    if delete_handler
                    else None
                )
                ctk.CTkButton(
                    item_frame,
                    text="Ⅹ",
                    width=28,
                    command=delete_cmd,
                    fg_color=self.PALETTE["error"],
                    text_color=self.PALETTE["on_error"],
                    hover_color=self.PALETTE["on_error_container"],
                ).grid(row=0, column=1, padx=(5, 0))

    def show_confirmation(self, title: str, message: str) -> bool:
        """Shows a confirmation dialog and returns the user's choice."""
        msg = CTkMessagebox(
            title=title,
            message=message,
            icon="warning",
            option_1="No",
            option_2="Yes",
            button_color=self.PALETTE["primary_container"],
            button_text_color=self.PALETTE["on_primary_container"],
        )
        return msg.get() == "Yes"

    def _animate_typing_indicator(self, dot_count=0):
        """Animates the 'ACE is typing...' indicator."""
        if not self._typing_animation_running:
            return

        new_dot_count = (dot_count + 1) % 4
        dots = "." * new_dot_count
        try:
            self._typing_indicator_label.configure(text=f"ACE is typing{dots}")
            self.root.after(500, lambda: self._animate_typing_indicator(new_dot_count))
        except (tk.TclError, AttributeError):
            self._typing_animation_running = False

    def _create_widgets(self):
        """Initialises the GUI components for the chat interface."""
        self.root.geometry("900x500")
        self.root.resizable(True, True)

        # Use grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)  # Sidebar column
        self.root.grid_columnconfigure(1, weight=1)  # Main chat area column

        self._create_sidebar(self.root, row=0, column=0, rowspan=2)
        self._create_chat_area(self.root, row=0, column=1)
        self._create_input_area(self.root, row=1, column=1)

    def _configure_tags(self):
        """Configures text styles for different senders."""
        # Use foreground color and justification to distinguish senders.

        # Configure YOU tag
        self.chat_display.tag_config(
            "YOU",
            foreground=self.SENDER_COLOURS["YOU"],
            justify=tk.RIGHT,
            rmargin=10,
            spacing3=10,  # Spacing after the line
        )
        # Configure ACE tag
        self.chat_display.tag_config(
            "ACE",
            foreground=self.SENDER_COLOURS["ACE"],
            lmargin1=10,
            lmargin2=10,
            spacing3=10,  # Spacing after the line
        )
        # Configure INFO tag
        self.chat_display.tag_config(
            "INFO",
            foreground=self.SENDER_COLOURS["INFO"],
            justify=tk.CENTER,
            spacing3=10,  # Spacing after the line
        )
        # Configure ERROR tag
        self.chat_display.tag_config(
            "ERROR",
            foreground=self.SENDER_COLOURS["ERROR"],
            lmargin1=10,
            lmargin2=10,
            spacing3=10,  # Spacing after the line
        )

    def _create_sidebar(self, parent, row, column, rowspan):
        """Creates the sidebar for conversation history."""
        history_container = ctk.CTkFrame(parent, fg_color=self.PALETTE["surface"])
        history_container.grid(
            row=row, column=column, rowspan=rowspan, sticky="nsw", padx=(10, 0), pady=10
        )
        history_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            history_container,
            text="History",
            font=("", 16, "bold"),
            text_color=self.PALETTE["on_surface"],
        ).grid(row=0, column=0, padx=10, pady=10)
        self._history_frame = ctk.CTkScrollableFrame(
            history_container, label_text="", fg_color=self.PALETTE["surface"]
        )
        self._history_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def _create_chat_area(self, parent, row, column):
        """Creates the chat display area using a CTkTextbox."""
        self.chat_display = ctk.CTkTextbox(
            parent,
            wrap=tk.WORD,
            state="disabled",
            font=("Segoe UI", 13),
            fg_color=self.PALETTE["surface"],
            text_color=self.PALETTE["on_surface"],
            border_color=self.PALETTE["outline"],
            border_width=1,
        )
        self.chat_display.grid(
            row=row, column=column, padx=(10, 10), pady=(10, 0), sticky="nsew"
        )

    def _create_input_area(self, parent, row, column):
        """Creates the user input area."""
        input_area = ctk.CTkFrame(parent, fg_color="transparent")
        input_area.grid(row=row, column=column, padx=10, pady=10, sticky="sew")
        input_area.grid_columnconfigure(0, weight=1)

        # Typing indicator (initially hidden)
        self._typing_indicator_label = ctk.CTkLabel(
            input_area, text="", text_color=self.PALETTE["on_surface_variant"]
        )
        self._typing_indicator_label.grid(
            row=0, column=0, columnspan=2, sticky="w", padx=5
        )
        self._typing_indicator_label.grid_remove()

        # Input Entry
        self.input_entry = ctk.CTkEntry(
            input_area,
            placeholder_text="Ask ACE...",
            fg_color=self.PALETTE["surface_variant"],
            text_color=self.PALETTE["on_surface"],
            border_color=self.PALETTE["outline"],
            placeholder_text_color=self.PALETTE["on_surface_variant"],
        )
        self.input_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.input_entry.bind("<Return>", self._send_message)

        # Send Button
        self.send_button = ctk.CTkButton(
            input_area,
            text="Send",
            width=70,
            command=self._send_message,
            fg_color=self.PALETTE["primary"],
            text_color=self.PALETTE["on_primary"],
            hover_color=self.PALETTE["primary_container"],
        )
        self.send_button.grid(row=1, column=1, sticky="e")

    def _send_message(self, event=None):
        """Handles sending a message."""
        message = self.get_user_input()
        if message:
            # Display the user's message immediately
            self.display_message("YOU", message)
            self.root.update_idletasks()  # Force immediate redraw
            self.scroll_to_bottom()

            # Reset input and schedule the handler to run after the UI has updated
            self.clear_input()
            self.root.after(
                10,
                lambda: self._input_handler(message) if self._input_handler else None,
            )
            self.input_entry.focus()

    def set_input_enabled(self, enabled: bool):
        """Enables or disables the input field and send button."""
        state = "normal" if enabled else "disabled"
        self.input_entry.configure(state=state)
        self.send_button.configure(state=state)

    def after(self, delay: int, callback: Callable):
        """Schedules a callback after a delay."""
        self.root.after(delay, callback)

    def track_action(
        self, action_func: Callable, description: str = "ACE is thinking..."
    ) -> Any:
        """Tracks a function with a visual indicator."""
        self.show_typing_indicator()
        self.root.update_idletasks()  # Ensure UI updates before blocking
        result = action_func()
        self.hide_typing_indicator()
        return result

    def reset_input(self):
        """Resets the input field to be empty and focused."""
        self.clear_input()
        self.input_entry.focus()

    def get_chat_history(self) -> List:
        """Returns the chat history as a list of strings."""
        return self.chat_history

    def get_conversation_history(self) -> List:
        """Returns a list of the conversation buttons from the sidebar."""
        history = []

        # Need to get the buttons from the sidebar which are inside separate items frames
        for widget in self._history_frame.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkButton) and "ID:" in child.cget("text"):
                    history.append(child)

        return history
