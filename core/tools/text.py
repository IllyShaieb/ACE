"""core.tools.text: Contains tools for text manipulation and analysis."""

from typing import Any, Dict, Optional


class CharacterCounterTool:
    """A tool that counts the number of characters in a given input string."""

    @property
    def name(self) -> str:
        """Return the name of the tool."""
        return "count_characters"

    @property
    def description(self) -> str:
        """Return a brief description of the tool's functionality."""
        return "Counts the number of characters in a given input string."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return a schema defining the parameters required by the tool."""
        return {
            "type": "OBJECT",
            "properties": {
                "input_string": {"type": "STRING"},
                "with_spaces": {
                    "type": "BOOLEAN",
                    "description": "Whether to count spaces as characters.",
                },
                "character": {
                    "type": "STRING",
                    "description": "Optional specific character to count (overrides with_spaces).",
                },
            },
            "required": ["input_string", "with_spaces"],
        }

    def execute(
        self,
        input_string: str,
        with_spaces: bool = True,
        character: Optional[str] = None,
    ) -> int:
        """Given an input string, count the number of characters based on the provided parameters.

        Args:
            input_string (str): The string to analyze.
            with_spaces (bool): Whether to count spaces as characters. Defaults to True.
            character (Optional[str]): If provided, counts only this specific character instead of all characters.

        Returns:
            int: The count of characters based on the specified parameters.
        """
        # If a specific character is provided, count only that character.
        if character is not None:
            return input_string.count(character)

        # Otherwise, count all characters, optionally excluding spaces.
        if not with_spaces:
            return len(input_string) - input_string.count(" ")

        return len(input_string)
