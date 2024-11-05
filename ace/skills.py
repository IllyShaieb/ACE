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


def who_are_you_skill(entities=None) -> str:
    """Explain who ACE is."""
    lines = [
        "I'm ACE, your Artificial Consciousness Engine.",
        "I'm here to help with things and tell you what's going on.",
        "You can ask me to do stuff for you, or just chat with me!",
    ]
    return " ".join(lines)


def how_are_you_skill(entities=None) -> str:
    """Ask ACE how it is doing."""
    lines = [
        "As an Artificial Consciousness Engine, I don't have feelings,",
        "but I'm ready to help you out. What can I do for you today?",
    ]
    return " ".join(lines)
