"""main.py - The entry point for the ACE program.

This file is used to start the ACE program and interact with the user,
linking together the various components of the program.

To run the program, simply execute this file using `uv`:
    $ uv run main.py

If you haven't installed `uv` yet, you can do so using pip:
    $ pip install uv
"""

from core import __version__, database as db
from core.input import text_input, InvalidInputError
from core.output import text_output
from core.model import ACEModel

ACE_ID: str = "ACE"
USER_ID: str = "YOU"
EXIT_COMMAND: str = "exit"

ACE_DATABASE: str = "data/ace.db"


def main():
    """The main entry point for the ACE program.

    This function connects the user input and program output with the
    various models, providing a simple conversational interface for the
    user to interact with the ACE program.
    """
    try:
        text_output(f"Creating database '{ACE_DATABASE}'...")
        db.create_database(ACE_DATABASE)
    except Exception as e:
        text_output(f"Error creating database: {e}")

    text_output(f" ACE v{__version__} ".center(80, "="), line_end="\n\n")
    ace_model = ACEModel()
    text_output(f"Type '{EXIT_COMMAND}' to exit.".center(80, " "), "\n\n")

    # Start the conversation
    chat_id = db.start_conversation(ACE_DATABASE)
    text_output(f"{ACE_ID}: Hello! I am ACE, how can I help you?")
    db.add_message(
        ACE_DATABASE, chat_id, ACE_ID, "Hello! I am ACE, how can I help you?"
    )
    while True:

        try:
            user_input = text_input(f"{USER_ID}: ")
            db.add_message(ACE_DATABASE, chat_id, USER_ID, user_input)

            if user_input.lower() == EXIT_COMMAND:
                text_output(f"{ACE_ID}: Goodbye!")
                db.add_message(ACE_DATABASE, chat_id, ACE_ID, "Goodbye!")
                break

            response = ace_model(user_input)
            db.add_message(ACE_DATABASE, chat_id, ACE_ID, response)
            text_output(f"{ACE_ID}: {response}")

        except InvalidInputError:
            text_output(f"{ACE_ID}: I'm ready. What's on your mind?")
            db.add_message(ACE_DATABASE, chat_id, USER_ID, "")
            db.add_message(
                ACE_DATABASE,
                chat_id,
                ACE_ID,
                "I'm ready. What's on your mind?",
            )
            continue


if __name__ == "__main__":
    main()
