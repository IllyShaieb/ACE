def skills() -> dict:
    """Return a dictionary of skills."""
    return {
        "dummy": dummy_skill,
    }


def dummy_skill(entities=None) -> str:
    """Dummy skill that does nothing. Used for testing."""
    if entities:
        return f"This dummy skill has the following entities: {entities}"
    return "This is a dummy skill. It does nothing."
