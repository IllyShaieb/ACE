"""view.py: Contains the view interfaces and implementations for the ACE program."""

import tkinter as tk
from datetime import datetime
from typing import Callable, List, Optional, Protocol, runtime_checkable

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

    def show_confirmation(self, title: str, message: str) -> bool:
        """Displays a confirmation dialog to the user.

        ### Args
            title (str): The title of the confirmation dialog.
            message (str): The message to display in the dialog.

        ### Returns
            bool: True if the user confirmed, False otherwise.
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

    def close(self):
        """Closes the console view.

        This method does nothing for console-based interaction, as there is no
        GUI to close.
        """
        pass

    def show_typing_indicator(self):
        """Informs the user that ACE is responding.

        TODO: Implement a visual indicator (e.g., spinner) to show that ACE is
            processing the request.
        """
        pass

    def hide_typing_indicator(self):
        """Hides the visual indicator for processing.

        TODO: Implement logic to hide the visual indicator (e.g., stop spinner)
            when ACE has finished processing the request.
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


class DesktopView(IACEView):
    """A concrete implementation of IACEView for desktop GUI interaction.

    This view creates a simple chat-style window. It is designed to be
    controlled by a Presenter, receiving display commands and reporting
    user input events.
    """

    SENDER_COLOURS = {
        "ACE": ("#1D1B20", "#FFFFFF"),  # (bg_color, fg_color)
        "ERROR": ("#8C1D18", "white"),
        "INFO": (None, "cyan"),  # No background for info messages
        "YOU": ("#6750A4", "white"),
    }

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("ACE")

        # Store the message history
        self._message_history = []
        self._message_widgets = []  # To store (widget, type) tuples
        self._history_buttons = []

        # User actions
        self.query_response = None
        self._typing_animation_running = False

        # Create the widgets and layout
        self._create_widgets()

        self._input_handler = None

    def run(self):
        """Starts the GUI event loop."""
        self.root.mainloop()

    def close(self):
        """Closes the GUI window."""
        try:
            self.root.update_idletasks()
            self.root.destroy()
        except tk.TclError:
            pass

    def set_input_handler(self, handler: Callable):
        """Sets the callback to be called when user submits input.

        This is required to handle user input asynchronously, allowing the Presenter to process
        the input without blocking the GUI.

        ### Args
            handler (callable): A function that takes the user's input as an argument.
        """
        self._input_handler = handler

    def get_user_input(self, prompt: str) -> str:
        """Gets user input from the input entry field.

        ### Args
            prompt (str): The prompt to display before awaiting input.

        ### Returns
            str: The user's input, stripped of leading/trailing whitespace.
        """
        return self.input_entry.get().strip()

    def get_chat_history(self) -> List:
        """Returns the chat history as a list of strings."""
        return self._message_history

    def clear_chat_history(self):
        """Clears the chat history."""
        self._message_history.clear()
        self._message_widgets.clear()

        # Destroy all message bubble widgets
        for widget in self.chat_frame.winfo_children():
            widget.destroy()

    def reset_input(self):
        """Resets the input entry field."""
        if hasattr(self, "input_entry"):
            self.input_entry.delete(0, tk.END)
            self.input_entry.configure(state=tk.NORMAL)

    def display_message(self, sender: str, message: str):
        """Displays a message in the chat window as a bubble.

        ### Args
            sender (str): The name of the sender
            message (str): The message content.
        """
        # Format the message and add it to the history
        formatted_message = self._format_message(sender, message)
        self._message_history.append(formatted_message.strip())

        # Get colours and alignment
        bg_color, fg_color = self.SENDER_COLOURS.get(
            sender.upper(), ("#333333", "white")
        )
        anchor = "e" if sender.upper() == "YOU" else "w"

        # INFO and ERROR messages are displayed differently
        if sender.upper() == "ERROR":
            # Create a frame with a red background for the error message
            error_frame = ctk.CTkFrame(
                self.chat_frame, fg_color=bg_color, corner_radius=10
            )
            error_label = ctk.CTkLabel(
                error_frame,
                text=message,
                text_color=fg_color,
                wraplength=self.root.winfo_width() - 100,
                justify=tk.LEFT,
            )
            error_label.pack(padx=10, pady=5)
            error_frame.pack(fill="x", padx=10, pady=5, anchor="w")
            self._message_widgets.append((error_label, "error"))

            self.root.update_idletasks()
            self._chat_scrollable_frame._parent_canvas.yview_moveto(1.0)
            return

        if sender.upper() == "INFO":
            info_label = ctk.CTkLabel(
                self.chat_frame,
                text=formatted_message.strip(),
                text_color=fg_color,
                wraplength=self.root.winfo_width() - 100,
            )
            info_label.pack(fill="x", padx=10, pady=5, anchor="w")
            self._message_widgets.append((info_label, sender.lower()))
            self.root.update_idletasks()
            self._chat_scrollable_frame._parent_canvas.yview_moveto(1.0)
            return

        # Create a bubble frame
        bubble = ctk.CTkFrame(self.chat_frame, fg_color=bg_color, corner_radius=10)

        # Create the message label inside the bubble
        label = ctk.CTkLabel(
            bubble,
            text=message,
            text_color=fg_color,
            wraplength=int(self.root.winfo_width() * 0.7),
            justify=tk.LEFT,
            anchor="w",
        )
        label.pack(padx=10, pady=5)
        self._message_widgets.append((label, "bubble"))

        # Set the bubble's horizontal alignment
        if anchor == "e":
            bubble.pack(fill="none", padx=(100, 10), pady=5, anchor=anchor)
        else:
            bubble.pack(fill="none", padx=(10, 100), pady=5, anchor=anchor)

        # Scroll to the bottom
        self.root.update_idletasks()
        self._chat_scrollable_frame._parent_canvas.yview_moveto(1.0)

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

    def show_typing_indicator(self):
        """Displays a visual indicator that the application is processing."""
        self.input_entry.configure(state="disabled")
        self.send_button.configure(text="...", state="disabled")

        # Create and display the "ACE is typing..." label
        self._typing_indicator_label = ctk.CTkLabel(
            self.chat_frame,
            text="ACE is typing",
            text_color="gray",
            anchor="center",
        )
        self._typing_indicator_label.pack(fill="x", padx=15, pady=5, anchor="center")

        # Start animation
        if not self._typing_animation_running:
            self._typing_animation_running = True
            self._animate_typing_indicator()

        # Scroll to the bottom to make the indicator visible
        self.root.update_idletasks()
        self._chat_scrollable_frame._parent_canvas.yview_moveto(1.0)

    def hide_typing_indicator(self):
        """Hides the visual indicator for processing."""
        self._typing_animation_running = False
        if hasattr(self, "_typing_indicator_label"):
            try:
                self._typing_indicator_label.destroy()
            except tk.TclError:
                pass  # Widget may already be destroyed
            del self._typing_indicator_label

        self.input_entry.configure(state="normal")
        self.send_button.configure(text="Send", state="normal")
        self.root.update_idletasks()

    def display_conversations(
        self,
        conversations: list,
        select_handler: Optional[Callable] = None,
        delete_handler: Optional[Callable] = None,
        new_chat_handler: Optional[Callable] = None,
    ):
        """Displays a list of past conversations in the sidebar.

        ### Args
            conversations (list): A list of (id, timestamp) tuples.
            select_handler (callable, optional): Handler for selecting a conversation.
            delete_handler (callable, optional): Handler for deleting a conversation.
            new_chat_handler (callable, optional): Handler for starting a new chat.
        """
        # Clear previous widgets from the frame
        for widget in self._history_frame.winfo_children():
            widget.destroy()
        self._history_buttons.clear()

        # Add "New Chat" button
        if new_chat_handler:
            new_chat_button = ctk.CTkButton(
                self._history_frame, text="+ New Chat", command=new_chat_handler
            )
            new_chat_button.pack(fill="x", padx=5, pady=(5, 10))

        # Add conversation buttons
        for conversation_id, timestamp in conversations:
            # Frame to hold conversation and delete buttons
            item_frame = ctk.CTkFrame(self._history_frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=5, pady=2)
            item_frame.grid_columnconfigure(0, weight=1)

            # Format timestamp for display
            dt = datetime.fromisoformat(timestamp)
            display_text = f"ID: {conversation_id}\n{dt.strftime('%Y-%m-%d %H:%M')}"

            select_btn = ctk.CTkButton(
                item_frame,
                text=display_text,
                command=(
                    (lambda cid=conversation_id: select_handler(cid))
                    if select_handler
                    else None
                ),
                anchor="w",
            )
            select_btn.grid(row=0, column=0, sticky="ew")
            self._history_buttons.append(select_btn)

            if delete_handler:
                delete_btn = ctk.CTkButton(
                    item_frame,
                    text="Ⅹ",
                    width=28,
                    command=(
                        (lambda cid=conversation_id: delete_handler(cid))
                        if delete_handler
                        else None
                    ),
                )
                delete_btn.grid(row=0, column=1, padx=(5, 0))

    def show_confirmation(self, title: str, message: str) -> bool:
        """Shows a confirmation dialog and returns the user's choice."""
        msg = CTkMessagebox(
            title=title, message=message, icon="warning", option_1="No", option_2="Yes"
        )
        return msg.get() == "Yes"

    def select_conversation_by_index(self, index: int):
        """Programmatically triggers a click on a conversation in the sidebar.

        Args:
            index (int): The index of the conversation to select.
        """
        if 0 <= index < len(self._history_buttons):
            self._history_buttons[index].invoke()
        else:
            raise IndexError("Conversation index out of range.")

    def get_conversation_history(self) -> list:
        """Return the items in the conversation history."""
        return self._history_buttons

    def _animate_typing_indicator(self, dot_count=0):
        """Animates the 'ACE is typing...' indicator."""
        if not self._typing_animation_running:
            return

        # Cycle through 0 to 3 dots
        new_dot_count = (dot_count + 1) % 4
        dots = "." * new_dot_count
        text = f"ACE is typing{dots}"

        try:
            if hasattr(self, "_typing_indicator_label"):
                self._typing_indicator_label.configure(text=text)
                # Schedule the next update
                self.root.after(
                    500, lambda: self._animate_typing_indicator(new_dot_count)
                )
        except (tk.TclError, AttributeError):
            # Stop animation if widget is destroyed
            self._typing_animation_running = False

    def _create_widgets(self):
        """Initialises the GUI components for the chat interface."""
        self.root.geometry("900x500")
        self.root.resizable(True, True)

        # Use grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)  # Sidebar column
        self.root.grid_columnconfigure(1, weight=1)  # Main chat area column

        # Create all the GUI components
        self._create_sidebar(self.root, row=0, column=0, rowspan=2)
        self._create_chat_area(self.root, row=0, column=1)
        self._create_input_area(self.root, row=1, column=1)

        # Bind the resize event
        self.root.bind("<Configure>", self._on_resize)

    def _on_resize(self, event=None):
        """Callback function to handle window resize events."""
        new_width = self.root.winfo_width()
        info_wraplength = new_width - 100
        bubble_wraplength = int(new_width * 0.7)
        error_wraplength = new_width - 100

        for widget, widget_type in self._message_widgets:
            try:
                if widget_type == "info":
                    widget.configure(wraplength=info_wraplength)
                elif widget_type == "error":
                    widget.configure(wraplength=error_wraplength)
                else:  # bubble
                    widget.configure(wraplength=bubble_wraplength)
            except tk.TclError:
                # Ignore errors for widgets that might have been destroyed
                pass

    def _create_sidebar(self, parent, row=0, column=0, rowspan=2):
        """Creates a sidebar for displaying past conversations and other information.

        ### Args
            parent: The parent widget to place the chat area in.
            row (int): The row index for grid placement.
            column (int): The column index for grid placement.
            rowspan (int): The number of rows to display the sidebar across
        """
        history_container = ctk.CTkFrame(parent)
        history_container.grid(
            row=row, column=column, rowspan=rowspan, sticky="nsw", padx=(20, 0), pady=20
        )
        history_container.grid_rowconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            history_container, text="History", font=("", 16, "bold")
        )
        title_label.grid(row=0, column=0, padx=10, pady=10)

        self._history_frame = ctk.CTkScrollableFrame(history_container, label_text="")
        self._history_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def _create_chat_area(self, parent, row=0, column=0):
        """Creates the chat display area.

        ### Args
            parent: The parent widget to place the chat area in.
            row (int): The row index for grid placement.
            column (int): The column index for grid placement.
        """
        self._chat_scrollable_frame = ctk.CTkScrollableFrame(parent)
        self._chat_scrollable_frame.grid(
            row=row,
            column=column,
            padx=20,
            pady=20,
            sticky="nsew",
        )
        # This inner frame will hold the message bubbles
        self.chat_frame = self._chat_scrollable_frame

    def _create_input_area(self, parent, row=1, column=0):
        """Creates the input area for user messages.

        ### Args
            parent: The parent widget to place the input area in.
            row (int): The row index for grid placement.
            column (int): The column index for grid placement.
        """

        self.root.bind("/", lambda event: self.input_entry.focus())

        # Configure a sub section for the input area
        self._input_area = ctk.CTkFrame(parent)
        self._input_area.grid(
            row=row,
            column=column,
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

            # Force the GUI to update so the user's message appears immediately
            self.root.update_idletasks()

            # Call the input handler with the user's message
            if self._input_handler and callable(self._input_handler):
                self._input_handler(message)

            # Focus back on the input entry
            try:
                self.input_entry.focus()
            except tk.TclError:
                pass

    def set_input_enabled(self, enabled: bool):
        """Enables or disables the input field and send button."""
        state = "normal" if enabled else "disabled"
        self.input_entry.configure(state=state)
        self.send_button.configure(state=state)
