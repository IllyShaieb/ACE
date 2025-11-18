"""view.py: Contains the view interfaces and implementations for the ACE program."""

import re
import sys
import tkinter as tk
from io import BytesIO
from queue import Queue
from threading import Thread
from typing import Any, Callable, List, Optional, Protocol, runtime_checkable

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageTk
from pylatexenc.latex2text import LatexNodes2Text
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Literal

# Add this import if you have matplotlib installed
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


class MathRenderer:
    """Renders LaTeX formulas to images for display in Tkinter."""

    def __init__(self, root: ctk.CTk, dpi: int = 120):
        if not plt:
            raise ImportError(
                "Matplotlib is not installed. Please install it with 'pip install matplotlib'."
            )
        self._root = root
        self._dpi = dpi
        self._photo_images = {}  # Cache PhotoImage objects

    def render(
        self, formula: str, text_color: str, is_inline: bool = False
    ) -> Optional[tk.PhotoImage]:
        """Renders a LaTeX formula to a PhotoImage."""
        cache_key = (formula, text_color, is_inline)
        if cache_key in self._photo_images:
            return self._photo_images[cache_key]

        try:
            # Adjust figure size and font size for inline formulas
            figsize = (0.8, 0.3) if is_inline else (6, 1)
            fontsize = 10 if is_inline else 13

            # Create a matplotlib figure with a smaller size
            fig = plt.figure(figsize=figsize, dpi=self._dpi)
            ax = fig.add_subplot(111)

            # Render the formula
            ax.text(
                0.5,
                0.5,
                f"${formula}$",
                size=fontsize,
                ha="center",
                va="center",
                color=text_color,
            )
            ax.axis("off")

            # Save to a BytesIO buffer with less padding
            buffer = BytesIO()
            fig.savefig(
                buffer,
                format="png",
                transparent=True,
                bbox_inches="tight",
                pad_inches=0,
            )
            buffer.seek(0)
            plt.close(fig)

            # Create a PhotoImage
            image = Image.open(buffer)
            photo = ImageTk.PhotoImage(image)
            self._photo_images[cache_key] = photo
            return photo

        except Exception:
            return None


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

    def display_history(self, messages: list[tuple[str, str]]):
        """
        Clears the current chat and displays a list of historical messages.

        ### Args:
            messages (list[tuple[str, str]]): A list of (sender, message) tuples.
        """


class ConsoleView(IACEView):
    """A console-based view for the ACE application."""

    # (border_colour, text_colour)
    SENDER_COLOURS = {
        "ACE": ("cyan", "cyan"),
        "ERROR": ("red", "red"),
        "INFO": ("white", "white"),
        "YOU": ("magenta", "magenta"),
    }

    def __init__(self):
        self.console = Console()
        self._current_ace_message = ""
        self._live_display = None
        self._latex_converter = LatexNodes2Text()

    def _preprocess_latex(self, text: str) -> str:
        """
        Finds LaTeX expressions in a string and converts them to plain text
        before Markdown parsing.

        ### Args
            text (str): The input text containing LaTeX expressions.

        ### Returns
            str: The text with LaTeX expressions converted to plain text.
        """
        # This pattern is more robust. It looks for $$...$$ blocks first,
        # then for non-greedy $...$ inline expressions. It avoids single
        # dollar signs that are not part of a pair.
        latex_pattern = re.compile(r"(\$\$[^\$]+\$\$|\$[^\$]+\$)")

        def replace_match(match):
            latex_code = match.group(1)
            # Convert to text. The converter expects the delimiters.
            text_representation = self._latex_converter.latex_to_text(latex_code)
            return text_representation

        return latex_pattern.sub(replace_match, text)

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
            # Create a Markdown object for the message content
            markdown = Markdown(self._preprocess_latex(message))

            panel = Panel(
                markdown,
                title=sender,
                border_style=border_colour,
                expand=False,
                title_align=justify,
            )
            self.console.print(panel, justify=justify, markup=True)

        self.chat_history.append((sender, message))

    def get_user_input(self, prompt: str) -> str:
        """Gets user input from the console.

        ### Args
            prompt (str): The prompt to display before input.

        ### Returns
            str: The user's input, with leading/trailing whitespace removed.
        """
        _, text_colour = self.SENDER_COLOURS["YOU"]

        # Print the prompt using rich, but get input using Python's built-in input()
        # to avoid issues with special characters in the user's typing.
        self.console.print(f"[bold {text_colour}]{prompt}[/bold {text_colour}]", end="")
        user_input = input().strip()

        # Store the original input to calculate lines for clearing
        self._last_input = prompt + user_input

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
        """
        Clears the last input line(s) from the console after submission.
        This version correctly handles multi-line input wrapping.
        """
        if not hasattr(self, "_last_input"):
            return

        # Calculate how many lines the last input took up
        prompt_and_input_length = len(self._last_input)
        terminal_width = self.console.width
        lines_to_clear = (prompt_and_input_length + terminal_width) // terminal_width

        # Move cursor up and clear each line
        for _ in range(lines_to_clear):
            sys.stdout.write("\x1b[1A")  # Move cursor up one line
            sys.stdout.write("\x1b[2K")  # Clear entire line

        # Position cursor at the beginning of the now-cleared line
        sys.stdout.write("\r")
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
            delete_handler (Optional[Callable]: A callback function to handle conversation deletion.
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
        """Forces the chat view to scroll to the latest message."""
        pass

    def display_history(self, messages: list[tuple[str, str]]):
        """Displays a list of historical messages in the console.

        ### Args
            messages (list[tuple[str, str]]): A list of (sender, message) tuples.
        """
        self.clear_chat_history()
        for sender, message in messages:
            self.display_message(sender, message)


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

        # Gracefully handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self._is_closing = False

        # For handling threaded actions
        self._action_queue = Queue()
        self._action_thread: Optional[Thread] = None
        self._action_completion_handler: Optional[Callable] = None

        # Initialize the math renderer
        self._math_renderer = MathRenderer(self.root) if plt else None

        # User actions
        self._input_handler = None
        self._typing_animation_running = False

        # Sidebar state
        self._all_conversations = []
        self._conversation_handlers = {}
        self._conversations_limit = 10
        self._current_page = 0

        # Create the widgets and layout
        self._create_widgets()
        self._configure_tags()

        self.chat_history = []  # Initialize chat history for DesktopView

        self._default_font = ctk.CTkFont(family="IBM Plex Sans", size=13)
        self.root.option_add("*Font", self._default_font)

        self._code_block_frames = []  # Track code block frames for cleanup

    def run(self):
        """Starts the GUI event loop."""
        self.root.mainloop()

    def close(self):
        """Closes the GUI window."""
        # Stop any running animations to prevent errors on exit.
        self._is_closing = True
        self._typing_animation_running = False

        # Wait for the action thread to finish if it's running
        if self._action_thread and self._action_thread.is_alive():
            self._action_thread.join(timeout=1.0)

        try:
            # Using quit() and destroy() for a cleaner shutdown
            self.root.quit()
            self.root.destroy()
        except tk.TclError:
            # This can happen if the window is already gone.
            pass

    def set_input_handler(self, handler: Callable):
        """Sets the callback for user input.

        ### Args
            handler (Callable): A function that takes the user's input as an argument.
        """
        self._input_handler = handler

    def get_user_input(self, prompt: Optional[str] = None) -> str:
        """Gets user input from the input entry field.

        ### Args
            prompt (Optional[str]): Ignored for GUI input.

        ### Returns
            str: The user's input, with leading/trailing whitespace removed.
        """
        user_input = self.input_entry.get().strip()

        # NOTE: This view does NOT immediately display the user message.
        # The presenter is responsible for that.
        self.chat_history.append(f"YOU: {user_input}")
        return user_input

    def clear_chat_history(self):
        """Clears the chat history from the textbox and destroys code block widgets."""
        # Destroy all code block frames
        for frame in getattr(self, "_code_block_frames", []):
            try:
                frame.destroy()
            except Exception:
                pass
        self._code_block_frames.clear()
        self.chat_display.delete("1.0", tk.END)
        self.chat_history = []

    def clear_input(self):
        """Clears the input entry field."""
        self.input_entry.delete(0, tk.END)

    def display_message(self, sender: str, message: str):
        """Displays a message in the chat window, parsing Markdown and LaTeX."""
        sender_tag = sender.upper()

        # Insert sender's name for ACE and YOU messages
        if sender_tag in ["ACE", "YOU"]:
            self.chat_display.insert(tk.END, f"{sender}\n", (sender_tag, "sender_name"))

        if sender_tag in ["ERROR", "INFO"]:
            # For ERROR and INFO, display the message plainly
            self.chat_display.insert(tk.END, message + "\n", (sender_tag,))
            self.chat_history.append(f"[{sender}] {message}")
            self.scroll_to_bottom()
            return

        # Handle multi-line code blocks first
        code_block_pattern = re.compile(r"```(.*?)```", re.DOTALL)
        last_end = 0
        for match in code_block_pattern.finditer(message):
            # Insert the non-code part before the match and parse it
            start, end = match.span()
            non_code_part = message[last_end:start]
            for line in non_code_part.split("\n"):
                self._parse_and_insert_line(line, (sender_tag,))
                self.chat_display.insert(tk.END, "\n")

            # Create and insert the code block widget
            code_content = match.group(1)
            self._create_code_block(code_content, sender_tag)
            last_end = end

        # Parse and insert any remaining text after the last code block
        remaining_text = message[last_end:]
        for line in remaining_text.split("\n"):
            self._parse_and_insert_line(line, (sender_tag,))
            self.chat_display.insert(tk.END, "\n")

        # Add final spacing and update history
        self.chat_display.insert(tk.END, "\n")
        self.chat_history.append(f"{sender}: {message}")
        self.scroll_to_bottom()

    def _parse_and_insert_line(self, text: str, base_tags: tuple):
        """Parses a single line for Markdown/LaTeX and inserts it."""
        # Regex for headers, bold, italic, code, and LaTeX
        pattern = re.compile(
            r"(?P<header>#+\s.*)|"
            r"(?P<latex_block>\$\$[^\$]+\$\$)|"
            r"(?P<latex_inline_paren>\(\$[^\$]+\$\))|"
            r"(?P<latex_inline>\$[^\$]+\$)|"
            r"(?P<bold>\*\*([^\*]+)\*\*)|"
            r"(?P<italic>\*([^\*]+)\*)|"
            r"(?P<code>`([^`]+)`)"
        )

        last_end = 0
        for match in pattern.finditer(text):
            # Insert the text before the match
            start, end = match.span()
            if start > last_end:
                self.chat_display.insert(tk.END, text[last_end:start], base_tags)

            last_end = end
            kind = match.lastgroup
            content = match.group(kind)
            tags = base_tags

            if kind == "header":
                level = len(content.split(" ")[0])
                if f"h{level}" in self.chat_display.tag_names():
                    tags += (f"h{level}",)
                self.chat_display.insert(tk.END, content.lstrip("# ").strip(), tags)
            elif kind == "latex_block":
                self._render_formula(content[2:-2], base_tags, is_block=True)
            elif kind == "latex_inline_paren":
                self._render_formula(content[2:-2], base_tags, is_block=False)
            elif kind == "latex_inline":
                self._render_formula(content[1:-1], base_tags, is_block=False)
            elif kind == "bold":
                # Recursively parse the content of the bold tag
                self._parse_and_insert_line(content[2:-2], base_tags + ("bold",))
            elif kind == "italic":
                # Recursively parse the content of the italic tag
                self._parse_and_insert_line(content[1:-1], base_tags + ("italic",))
            elif kind == "code":
                tags += ("code",)
                self.chat_display.insert(tk.END, content[1:-1], tags)

        # Insert any remaining text after the last match
        if last_end < len(text):
            self.chat_display.insert(tk.END, text[last_end:], base_tags)

    def _render_formula(self, formula: str, base_tags: tuple, is_block: bool):
        """Renders a LaTeX formula and inserts it into the text widget."""
        if not self._math_renderer:
            self.chat_display.insert(tk.END, f"[{formula}]", base_tags + ("italic",))
            return

        text_color = self.chat_display.tag_cget(base_tags[0], "foreground")
        formula_image = self._math_renderer.render(
            formula, text_color, is_inline=not is_block
        )

        if formula_image:
            if is_block:
                # For block formulas, add newlines for spacing and remove padx
                self.chat_display.insert(tk.END, "\n")
                self.chat_display.image_create(tk.END, image=formula_image, padx=0)
                self.chat_display.insert(tk.END, "\n")
            else:
                # For inline formulas, keep them in the line
                self.chat_display.image_create(
                    tk.END, image=formula_image, padx=0, pady=0
                )
        else:
            # Fallback to text if rendering fails
            self.chat_display.insert(
                tk.END, f" [Formula: {formula}] ", base_tags + ("italic",)
            )

    def display_history(self, messages: list[tuple[str, str]]):
        """
        Clears the current chat and displays a list of historical messages.
        This method is optimized for performance by batching UI updates.
        """
        # Hide the widget and disable updates to speed up insertion
        self.chat_display.grid_remove()
        self.chat_display.delete("1.0", tk.END)
        self.chat_history = []

        # This internal method contains the core logic of display_message
        # but is adapted for batch processing.
        def _insert_single_message(sender: str, message: str):
            sender_tag = sender.upper()
            self.chat_history.append(f"{sender}: {message}")

            if sender_tag in ["ACE", "YOU"]:
                self.chat_display.insert(
                    tk.END, f"{sender}\n", (sender_tag, "sender_name")
                )

            code_block_pattern = re.compile(r"```(.*?)```", re.DOTALL)
            last_end = 0
            for match in code_block_pattern.finditer(message):
                start, end = match.span()
                non_code_part = message[last_end:start]
                for line in non_code_part.split("\n"):
                    self._parse_and_insert_line(line, (sender_tag,))
                    self.chat_display.insert(tk.END, "\n")

                # Create and insert the code block widget
                code_content = match.group(1)
                self._create_code_block(code_content, sender_tag)
                last_end = end

            remaining_text = message[last_end:]
            for line in remaining_text.split("\n"):
                self._parse_and_insert_line(line, (sender_tag,))
                self.chat_display.insert(tk.END, "\n")

            self.chat_display.insert(tk.END, "\n")

        # Process all messages without updating the UI for each one
        for sender, message in messages:
            _insert_single_message(sender, message)

        # Re-enable the widget, show it, and scroll to the end
        self.chat_display.grid()  # Show the widget again
        self.scroll_to_bottom()

    def _create_code_block(self, code_content: str, sender_tag: str):
        """Creates and inserts a code block with a copy button that fills the chat width."""
        # Clean up code content
        if code_content.startswith("\n"):
            code_content = code_content[1:]
        if code_content.endswith("\n"):
            code_content = code_content[:-1]

        # Create a frame to hold the code and copy button
        code_frame = ctk.CTkFrame(
            self.chat_display,
            fg_color=self.PALETTE["surface_variant"],
            border_width=0,
        )
        # Track the frame for later destruction
        self._code_block_frames.append(code_frame)

        code_frame.grid_columnconfigure(0, weight=1)

        # Create the copy button
        copy_button = ctk.CTkButton(
            code_frame,
            text="📋",  # Clipboard emoji
            width=30,
            fg_color="transparent",
            text_color=self.PALETTE["on_surface_variant"],
            hover_color=self.PALETTE["surface"],
        )
        copy_button.grid(row=0, column=1, sticky="ne", padx=5, pady=5)

        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(code_content)
            original_text = copy_button.cget("text")
            copy_button.configure(text="Copied!")
            self.root.after(1500, lambda: copy_button.configure(text=original_text))

        copy_button.configure(command=copy_to_clipboard)

        # Create a textbox for the code
        code_textbox = ctk.CTkTextbox(
            code_frame,
            fg_color="transparent",
            text_color=self.SENDER_COLOURS.get(sender_tag, self.PALETTE["on_surface"]),
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none",  # Disable word wrap for code
            corner_radius=0,
            border_width=0,
        )
        code_textbox.insert("1.0", code_content)
        code_textbox.configure(state="disabled")  # Make it read-only
        code_textbox.grid(row=0, column=0, sticky="nsew", padx=(10, 40), pady=10)

        # Adjust frame height based on code content
        code_textbox.update_idletasks()
        lines = int(code_textbox.index("end-1c").split(".")[0])
        height = min(lines, 25) * 20 + 20  # Approx 20px per line, max 25 lines visible
        code_textbox.configure(height=height)

        # Embed the frame into the main chat display
        self.chat_display.window_create(
            tk.END, window=code_frame, stretch=1, align="center"
        )
        self.chat_display.insert(tk.END, "\n")

    def scroll_to_bottom(self):
        """Forces the chat view to scroll to the latest message."""
        self.chat_display.see(tk.END)

    def show_error(self, message: str):
        """Displays an error message.

        ### Args
            message (str): The error message to display.
        """
        self.display_message("ERROR", message)
        CTkMessagebox(
            title="Error",
            message=message,
            icon="cancel",
            button_color=self.PALETTE["error_container"],
            button_text_color=self.PALETTE["on_error_container"],
        )

    def show_info(self, message: str):
        """Displays an informational message.

        ### Args
            message (str): The informational message to display.
        """
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
        """
        Stores conversation data and updates the sidebar display.

        Args:
            conversations (list): A list of (conversation_id, timestamp) tuples.
            select_handler (Optional[Callable]): Callback for selection.
            delete_handler (Optional[Callable]): Callback for deletion.
            new_chat_handler (Optional[Callable]): Callback for new chat.
        """
        self._all_conversations = conversations
        self._conversation_handlers = {
            "select": select_handler,
            "delete": delete_handler,
            "new_chat": new_chat_handler,
        }
        self._current_page = 0  # Reset to the first page
        self._update_conversation_display()

    def _update_conversation_display(self):
        """Renders the conversation list in the sidebar with pagination."""
        for widget in self._history_frame.winfo_children():
            widget.destroy()

        new_chat_handler = self._conversation_handlers.get("new_chat")
        if new_chat_handler:
            ctk.CTkButton(
                self._history_frame,
                text="+ New Chat",
                command=new_chat_handler,
                fg_color=self.PALETTE["primary_container"],
                text_color=self.PALETTE["on_primary_container"],
                hover_color=self.PALETTE["primary"],
            ).pack(fill="x", padx=5, pady=(5, 10))

        # Pagination logic
        start_index = self._current_page * self._conversations_limit
        end_index = start_index + self._conversations_limit
        conversations_to_display = self._all_conversations[start_index:end_index]

        for conversation_id, name, timestamp in conversations_to_display:
            self._create_conversation_item(conversation_id, name, timestamp)

        # Pagination controls
        total_conversations = len(self._all_conversations)
        if total_conversations > self._conversations_limit:
            self._create_pagination_controls(total_conversations, end_index)

    def _create_pagination_controls(self, total_conversations: int, end_index: int):
        """Creates and packs the pagination buttons."""
        controls_frame = ctk.CTkFrame(self._history_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=5, pady=5, side="bottom")

        # Previous Button
        if self._current_page > 0:
            ctk.CTkButton(
                controls_frame,
                text="←",
                command=self._previous_page,
                fg_color=self.PALETTE["tertiary_container"],
                text_color=self.PALETTE["on_tertiary_container"],
                hover_color=self.PALETTE["tertiary"],
            ).pack(side="left", expand=True, padx=2)

        # Next Button
        if end_index < total_conversations:
            ctk.CTkButton(
                controls_frame,
                text="→",
                command=self._next_page,
                fg_color=self.PALETTE["tertiary_container"],
                text_color=self.PALETTE["on_tertiary_container"],
                hover_color=self.PALETTE["tertiary"],
            ).pack(side="right", expand=True, padx=2)

        # Back to Top Button
        if self._current_page > 0:
            ctk.CTkButton(
                self._history_frame,
                text="Back to Top",
                command=self._go_to_first_page,
                fg_color="transparent",
                text_color=self.PALETTE["on_surface_variant"],
                hover_color=self.PALETTE["surface_variant"],
            ).pack(fill="x", padx=5, pady=(5, 0), side="bottom")

    def _previous_page(self):
        """Navigates to the previous page of conversations."""
        if self._current_page > 0:
            self._current_page -= 1
            self._update_conversation_display()

    def _next_page(self):
        """Navigates to the next page of conversations."""
        if (self._current_page + 1) * self._conversations_limit < len(
            self._all_conversations
        ):
            self._current_page += 1
            self._update_conversation_display()

    def _go_to_first_page(self):
        """Navigates back to the first page of conversations."""
        self._current_page = 0
        self._update_conversation_display()

    def _create_conversation_item(
        self, conversation_id: str, name: str, timestamp: str
    ):
        """Creates a single conversation item widget in the sidebar."""
        select_handler = self._conversation_handlers.get("select")
        delete_handler = self._conversation_handlers.get("delete")

        item_frame = ctk.CTkFrame(self._history_frame, fg_color="transparent")
        item_frame.pack(fill="x", padx=5, pady=2)
        item_frame.grid_columnconfigure(0, weight=1)

        select_cmd = (
            (lambda cid=conversation_id: select_handler(cid))
            if select_handler
            else None
        )
        conversation_button = ctk.CTkButton(
            item_frame,
            text=name,
            command=select_cmd,
            anchor="w",
            fg_color=self.PALETTE["secondary_container"],
            text_color=self.PALETTE["on_secondary_container"],
            hover_color=self.PALETTE["secondary"],
            font=ctk.CTkFont(family="IBM Plex Sans", size=12, weight="bold"),
            width=220,
        )
        conversation_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

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
        """Shows a confirmation dialog and returns the user's choice.

        ### Args
            title (str): The title of the confirmation dialog.
            message (str): The message to display in the dialog.

        ### Returns
            bool: True if the user confirmed, False otherwise.
        """
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
        """Animates the 'ACE is typing...' indicator.

        ### Args
            dot_count (int): The current number of dots to display.
        """
        if not self._typing_animation_running:
            return

        new_dot_count = (dot_count + 1) % 4
        dots = "." * new_dot_count
        try:
            self._typing_indicator_label.configure(text=f"ACE is typing{dots}")
            # Only schedule the next animation frame if not closing
            if not self._is_closing:
                self.root.after(
                    500, lambda: self._animate_typing_indicator(new_dot_count)
                )
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
        """Configures text styles for different senders in the tk.Text widget."""
        # Base font
        default_font = ctk.CTkFont(family="IBM Plex Sans", size=13)
        bold_font = ctk.CTkFont(family="IBM Plex Sans", size=13, weight="bold")
        italic_font = ctk.CTkFont(family="IBM Plex Sans", size=13, slant="italic")
        code_font = ctk.CTkFont(family="Consolas", size=12)

        # Header fonts
        h1_font = ctk.CTkFont(family="IBM Plex Sans", size=20, weight="bold")
        h2_font = ctk.CTkFont(family="IBM Plex Sans", size=16, weight="bold")
        h3_font = ctk.CTkFont(family="IBM Plex Sans", size=14, weight="bold")

        # Sender name font
        sender_name_font = ctk.CTkFont(family="IBM Plex Sans", size=13, weight="bold")

        # Sender tags
        self.chat_display.tag_config(
            "YOU",
            foreground=self.SENDER_COLOURS["YOU"],
            justify=tk.RIGHT,
            rmargin=10,
            spacing3=5,
            font=default_font,
        )
        self.chat_display.tag_config(
            "ACE",
            foreground=self.SENDER_COLOURS["ACE"],
            lmargin1=10,
            lmargin2=10,
            spacing3=5,
            font=default_font,
        )
        self.chat_display.tag_config(
            "INFO",
            foreground=self.SENDER_COLOURS["INFO"],
            justify=tk.CENTER,
            spacing3=5,
            font=italic_font,
        )
        self.chat_display.tag_config(
            "ERROR",
            foreground=self.SENDER_COLOURS["ERROR"],
            lmargin1=10,
            lmargin2=10,
            spacing3=5,
            font=default_font,
        )

        # Formatting tags
        self.chat_display.tag_config("sender_name", font=sender_name_font)
        self.chat_display.tag_config("bold", font=bold_font)
        self.chat_display.tag_config("italic", font=italic_font)
        self.chat_display.tag_config(
            "code",
            font=code_font,
            background=self.PALETTE["surface_variant"],
            lmargin1=10,
            lmargin2=10,
        )
        self.chat_display.tag_config("h1", font=h1_font, spacing1=10)
        self.chat_display.tag_config("h2", font=h2_font, spacing1=8)
        self.chat_display.tag_config("h3", font=h3_font, spacing1=6)

    def _create_sidebar(self, parent: ctk.CTk, row: int, column: int, rowspan: int):
        """Creates the sidebar for conversation history.

        ### Args
            parent (ctk.CTk): The parent widget.
            row (int): The row position in the grid.
            column (int): The column position in the grid.
            rowspan (int): The number of rows the sidebar should span.
        """
        SIDEBAR_WIDTH = 260  # Increase this value for a wider sidebar

        history_container = ctk.CTkFrame(
            parent, fg_color=self.PALETTE["surface"], width=SIDEBAR_WIDTH
        )
        history_container.grid(
            row=row, column=column, rowspan=rowspan, sticky="nsew", padx=(5, 0), pady=5
        )
        history_container.grid_rowconfigure(1, weight=1)
        history_container.grid_columnconfigure(0, minsize=SIDEBAR_WIDTH)

        ctk.CTkLabel(
            history_container,
            text="History",
            font=("", 16, "bold"),
            text_color=self.PALETTE["on_surface"],
        ).grid(row=0, column=0, padx=10, pady=10)
        self._history_frame = ctk.CTkScrollableFrame(
            history_container,
            label_text="",
            fg_color=self.PALETTE["surface"],
            width=SIDEBAR_WIDTH,
        )
        self._history_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def _create_chat_area(self, parent: ctk.CTk, row: int, column: int):
        """Creates the chat display area using a standard tk.Text widget."""
        chat_frame = ctk.CTkFrame(
            parent,
            fg_color=self.PALETTE["surface"],
            border_color=self.PALETTE["surface"],
            border_width=0,
            corner_radius=0,
        )
        chat_frame.grid(
            row=row, column=column, padx=(10, 10), pady=(10, 0), sticky="nsew"
        )
        chat_frame.grid_rowconfigure(0, weight=1)  # Textbox row expands
        chat_frame.grid_columnconfigure(0, weight=1)  # Textbox column expands
        chat_frame.grid_columnconfigure(1, weight=0)  # Button column does not expand

        self.chat_display = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            bg=self.PALETTE["surface"],
            fg=self.PALETTE["on_surface"],
            padx=10,
            pady=10,
            relief="flat",
            selectbackground=self.PALETTE["primary_container"],
            selectforeground=self.PALETTE["on_primary_container"],
            inactiveselectbackground=self.PALETTE["secondary_container"],
            borderwidth=0.5,
            highlightthickness=0,
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew")
        self.chat_display.bind("<KeyPress>", self._prevent_modification)
        self.chat_display.bind("<FocusIn>", self._defocus_chat_display)

        self.copy_conversation_button = ctk.CTkButton(
            chat_frame,
            text="📋 Copy Conversation",
            width=140,
            fg_color="transparent",
            text_color=self.PALETTE["on_surface_variant"],
            hover_color=self.PALETTE["surface_variant"],
            font=ctk.CTkFont(family="IBM Plex Sans", size=11),
            command=self._copy_conversation_to_clipboard,
            corner_radius=14,
            border_width=0.5,
            border_color=self.PALETTE["outline"],
        )
        self.copy_conversation_button.grid(
            row=0, column=1, sticky="ne", padx=(0, 5), pady=(5, 0)
        )

    def _copy_conversation_to_clipboard(self):
        """Copies the entire chat history to the clipboard."""
        # Join all chat history entries with newlines
        conversation_text = "\n".join(self.chat_history)
        self.root.clipboard_clear()
        self.root.clipboard_append(conversation_text)
        # Optionally, show a subtle feedback
        original_text = self.copy_conversation_button.cget("text")
        self.copy_conversation_button.configure(text="✔ Copied!")
        self.root.after(
            1200, lambda: self.copy_conversation_button.configure(text=original_text)
        )

    def _prevent_modification(self, event: Optional[tk.Event] = None) -> str:
        """Prevents the user from modifying the text in the chat display."""
        return "break"

    def _defocus_chat_display(self, event: Optional[tk.Event] = None):
        """Moves focus away from the chat display to the input entry."""
        self.input_entry.focus()

    def _create_input_area(self, parent: ctk.CTk, row: int, column: int):
        """Creates the user input area.

        ### Args
            parent (ctk.CTk): The parent widget.
            row (int): The row position in the grid.
            column (int): The column position in the grid.
        """
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

    def _send_message(self, event: Optional[tk.Event] = None):
        """Handles sending a message.

        ### Args
            event (Optional[tk.Event]): The event that triggered the send (if any).
        """
        message = self.get_user_input()
        if message:
            # NOTE: This view does not display the user message here.
            # The Presenter's process_user_input is responsible for it.
            self.root.update_idletasks()
            self.scroll_to_bottom()

            # Reset input and schedule the handler to run after the UI has updated
            self.clear_input()
            self.root.after(
                10,
                lambda: self._input_handler(message) if self._input_handler else None,
            )
            self.input_entry.focus()

    def set_input_enabled(self, enabled: bool):
        """Enables or disables the input field and send button.

        ### Args
            enabled (bool): True to enable input, False to disable.
        """
        state = "normal" if enabled else "disabled"
        self.input_entry.configure(state=state)
        self.send_button.configure(state=state)

    def after(self, delay: int, callback: Callable):
        """Schedules a callback after a delay.

        ### Args
            delay (int): The delay in milliseconds before calling the callback.
            callback (Callable): The function to call after the delay.
        """
        self.root.after(delay, callback)

    def track_action(
        self,
        action_func: Callable,
        on_complete: Callable,
        description: str = "ACE is thinking...",
    ):
        """
        Tracks a function with a visual indicator by running it in a background
        thread and calling a handler upon completion.
        """
        self.show_typing_indicator()
        self.root.update_idletasks()
        self._action_completion_handler = on_complete

        def action_wrapper():
            try:
                result = action_func()
                self._action_queue.put(("result", result))
            except Exception as e:
                self._action_queue.put(("error", e))

        # Clear previous results from the queue
        while not self._action_queue.empty():
            self._action_queue.get()

        self._action_thread = Thread(target=action_wrapper, daemon=True)
        self._action_thread.start()
        self._check_action_queue()

    def _check_action_queue(self):
        """Polls the queue for results from the background action thread."""
        if self._is_closing:
            return

        try:
            message_type, payload = self._action_queue.get_nowait()

            self.hide_typing_indicator()

            if self._action_completion_handler:
                self._action_completion_handler(payload, message_type == "error")

        except Exception:  # Queue is empty
            self.root.after(100, self._check_action_queue)

    def reset_input(self):
        """Resets the input field to be empty and focused."""
        self.clear_input()
        self.input_entry.focus()

    def get_chat_history(self) -> List:
        """Returns the chat history as a list of strings."""
        return self.chat_history

    def get_conversation_history(self) -> List:
        """Returns a list of the conversation buttons from the sidebar."""
        return self._all_conversations
