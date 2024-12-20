"""
This file is the main entry point for the ACE digital assistant.

It runs the main processing loop that interacts with the user,
processes their input, and executes the appropriate skills.
"""

from ace import ACE_LOGGING_LEVEL, __version__, brain, create_logger

# Logger must be created here to ensure that it can be used in all functions
logger = create_logger(__name__, ACE_LOGGING_LEVEL)


def main() -> None:
    """
    Launches the ACE digital assistant.

    This function runs the main processing loop for the ACE digital assistant.
    """

    logger.info(f"Running ACE - v{__version__} - Log level: {ACE_LOGGING_LEVEL}")

    # Display a welcome message
    print(" Welcome to ACE! ".center(80, "-"))
    print("Type 'q' to quit the program.\n")

    # Main processing loop
    try:
        while True:
            # Get user input and process it
            user_input = brain.get_user_input()
            processed_input = brain.process_user_input(user_input)

            # Check if the user wants to quit
            if processed_input == "q":
                logger.info("User exited the program by using: 'q'")
                print("ACE: Goodbye!")
                break

            # Recognise the intent, extract entities, and select the appropriate skill
            intent = brain.recognise_intent(processed_input)

            if intent:
                entities = brain.extract_entities(processed_input, intent)
                selected_skill = brain.select_skill(intent)

                try:  # Handle exceptions within individual skills
                    response = selected_skill(entities=entities)
                    print(f"ACE: {response}")
                except Exception as e:
                    logger.exception(
                        f"An error occurred in skill '{selected_skill.__name__}': {e}"
                    )
                    print("ACE: An error occurred while processing your request.")

            else:
                print("ACE: I'm sorry, I don't understand that.")

    except KeyboardInterrupt:
        if ACE_LOGGING_LEVEL == "INFO":
            error_message = "User exited the program"
        else:
            error_message = "User exited the program by pressing: Ctrl+C"

        logger.info(error_message)
        print("\nACE: Goodbye!")


# Entry point for the ACE digital assistant
if __name__ == "__main__":
    main()
