"""
This file is the main entry point for the ACE digital assistant.

It runs the main processing loop that interacts with the user,
processes their input, and executes the appropriate skills.
"""

from ace import brain


def main() -> None:
    """Runs the main processing loop for the ACE digital assistant."""

    # Display a welcome message
    print(" Welcome to ACE! ".center(80, "-"))
    print("Type 'q' to quit the program.\n")

    while True:
        # Get user input and process it
        user_input = brain.get_user_input()
        processed_input = brain.process_user_input(user_input)

        # Check if the user wants to quit
        if processed_input == "q":
            print("ACE: Goodbye!")
            break

        # Recognise the intent, extract entities, and select the appropriate skill
        intent = brain.recognise_intent(processed_input)

        if intent:
            entities = brain.extract_entities(processed_input, intent)
            selected_skill = brain.select_skill(intent)
            response = selected_skill(entities=entities)
            print(f"ACE: {response}")
        else:
            print("ACE: I'm sorry, I don't understand that.")


if __name__ == "__main__":
    main()
