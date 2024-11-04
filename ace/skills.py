def dummy_skill(entities=None) -> str:
    """Dummy skill that does nothing. Used for testing."""
    if entities:
        return f"This dummy skill has the following entities: {entities}"
    return "This is a dummy skill. It does nothing."


def greeting_skill(entities=None) -> str:
    """Greeting the user."""
    return "Hello! How can I help you?"


def farewell_skill(entities=None) -> str:
    """Say goodbye to the user."""
    return "Goodbye!"
