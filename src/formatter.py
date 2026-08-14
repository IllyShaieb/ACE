"""The formatter module provides utility functions for formatting text in the application."""

import markdown


def markdown_to_html(text: str) -> str:
    """Convert markdown text to HTML.

    Args:
        text (str): The markdown text to convert.

    Returns:
        str: The converted HTML text.
    """
    return markdown.markdown(text, extensions=["fenced_code", "tables", "nl2br"])
