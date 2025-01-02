"""models.py: Contains the main models for the ACE program.

This module contains the main models for the ACE program, which help
the program to understand and respond to user input.

classes:
- ACEModel: The main model for the ACE program.
"""


class ACEModel:
    """The main model for the ACE program.

    This class contains methods to process user input and generate responses
    based on the input.

    methods:
    - query: Processes the user's input and generates a response.
    """

    def query(self, user_input: str) -> str:
        """Processes the user's input and generates a response.

        Args:
            user_input (str): The user's input to process.

        Returns:
            str: The response generated by the model.
        """
        return "Sorry, I don't understand."
