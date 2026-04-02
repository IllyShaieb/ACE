"""core.tools.games: Defines game-related tools that ACE can use."""

import random
from typing import Any, Dict, List, Optional, Tuple


class CoinFlipTool:
    """A tool that simulates flipping a coin and returns the result."""

    @property
    def name(self) -> str:
        """Return the name of the tool."""
        return "flip_coin"

    @property
    def description(self) -> str:
        """Return a brief description of the tool's functionality."""
        return "Simulates flipping a coin and returns 'Heads' or 'Tails'."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return a schema defining the parameters required by the tool."""
        return {
            "type": "OBJECT",
            "properties": {
                "times": {
                    "type": "INTEGER",
                    "description": "The number of times to flip the coin. Defaults to 1.",
                }
            },
            "required": [],
        }

    def execute(self, times: int = 1, **kwargs: Any) -> List[str]:
        """Simulate flipping a coin a specified number of times and return the results.

        Args:
            times (int): The number of times to flip the coin. Defaults to 1.

        Returns:
            List[str]: A list of results for each coin flip, either 'Heads' or 'Tails'.
        """
        if times < 1:
            return []

        return [random.choice(["Heads", "Tails"]) for _ in range(times)]


class RollDiceTool:
    """A tool that simulates rolling a six-sided die and returns the result."""

    @property
    def name(self) -> str:
        """Return the name of the tool."""
        return "roll_dice"

    @property
    def description(self) -> str:
        """Return a brief description of the tool's functionality."""
        return "Simulates rolling a number of dice with the given number of sides"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return a schema defining the parameters required by the tool."""
        return {
            "type": "OBJECT",
            "properties": {
                "dice": {
                    "type": "ARRAY",
                    "description": "A list of dice to roll, where each die is represented as a string like 'd6' or 'd20'. Defaults to 1d6.",
                    "items": {"type": "STRING", "pattern": "^d\\d+$"},
                }
            },
            "required": [],
        }

    def execute(
        self, dice: Optional[List[str]] = None, **kwargs: Any
    ) -> List[Tuple[str, List[int]]]:
        """Simulate rolling a number of dice with the given number of sides.

        Args:
            dice (Optional[List[str]]): A list of dice to roll, where each die is represented
                as a string like 'd6' or 'd20'. Defaults to 1d6.

        Returns:
            List[Tuple[str, List[int]]]: A list of tuples, where each tuple contains the die
                type and the result of all the rolls.
        """
        # If no dice are specified, default to rolling one six-sided die (1d6).
        dice = dice or ["1d6"]

        # Loop through the list of dice
        results = []
        for die in dice:
            # Parse the die string (e.g., '2d10' means rolling 2 ten-sided dice)
            count_str, sides_str = die.lower().split("d")
            count = int(count_str) if count_str else 1  # Default to 1
            sides = int(sides_str)

            # Roll the specified number of dice and store the results
            dice_results = [random.randint(1, sides) for _ in range(count)]

            results.append((die, dice_results))

        return results
