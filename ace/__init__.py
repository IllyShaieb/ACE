from ace import skills  # noqa: F401

# Define the version of the ACE program. Must be in the format YYYY.MM.PATCH.
__version__ = "2024.11.0"

# Automatically create a skills configuration dictionary from the skills module.
# This allows the skills to be easily imported and used in the brain module.
skills_dict = {
    attr.upper(): getattr(skills, attr)
    for attr in dir(skills)
    if callable(getattr(skills, attr)) and attr.endswith("skill")
}
