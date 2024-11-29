"""
This file is the main entry point for the ACE digital assistant.

It runs the main processing loop that interacts with the user,
processes their input, and executes the appropriate skills.
"""

import argparse

from ace import __version__, brain, create_logger


def main(log_level: str = "INFO") -> None:
    """Launches the ACE digital assistant.

    This function runs the main processing loop for the ACE digital assistant.

    Args:
        log_level: The logging level to use (default is "INFO").
    """

    # Create a logger and display the program information
    logger = create_logger(__name__, log_level)
    logger.info(f"Running ACE - v{__version__} - Log level: {log_level}")

    # Display a welcome message
    print(" Welcome to ACE! ".center(80, "-"))
    print("Type 'q' to quit the program.\n")

    # Main processing loop
    try:

        while True:
            # Get user input and process it
            user_input = brain.get_user_input()
            logger.info(f"User input: {user_input}")
            processed_input = brain.process_user_input(user_input)

            # Check if the user wants to quit
            if processed_input == "q":
                logger.info("User exited the program by using: 'q'")
                print("ACE: Goodbye!")
                break

            # Recognise the intent, extract entities, and select the appropriate skill
            intent = brain.recognise_intent(processed_input)
            logger.info(f"Recognised intent: {intent}")

            if intent:
                entities = brain.extract_entities(processed_input, intent)
                logger.info(f"Extracted entities: {entities}")

                selected_skill = brain.select_skill(intent)
                response = selected_skill(entities=entities)
                print(f"ACE: {response}")

            else:
                logger.warning(f"Unrecognised intent for: {processed_input}")
                print("ACE: I'm sorry, I don't understand that.")

    except KeyboardInterrupt:
        if log_level == "INFO":
            error_message = "User exited the program"
        else:
            error_message = "User exited the program by pressing: Ctrl+C"

        logger.info(error_message)
        print("\nACE: Goodbye!")


if __name__ == "__main__":
    # Get the log level from the command line arguments
    description = [
        f"ACE (v{__version__})",
        "the Artificial Consciousness Engine, is a digital assistant.",
        "It is designed to help you with your daily tasks and keep you in the loop with your life and the world.",
    ]
    parser = argparse.ArgumentParser(description=" ".join(description))

    parser.add_argument(
        "-l",
        "--log-level",
        dest="log_level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default is INFO).",
    )

    args = parser.parse_args()

    # Run the main processing loop
    main(log_level=args.log_level)
