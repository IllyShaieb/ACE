from ace import brain


def main() -> None:
    """Run the ACE program."""
    print(" Welcome to ACE! ".center(80, "-"))
    print("Type 'q' to quit the program.\n")

    while True:
        user_input = brain.get_user_input()
        processed_input = brain.process_user_input(user_input)

        if processed_input == "q":
            print("ACE: Goodbye!")
            break

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
