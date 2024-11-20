"""
This is the main package for the ACE digital assistant.

It initialises the `skills_dict` dictionary, which maps intent names
to their corresponding skill functions. This dictionary is used by the
`brain` module to select and execute the appropriate skill based on the
user's intent.
"""

from ace import skills

# Define the version of the ACE program. Must be in the format YYYY.MM.PATCH.
__version__ = "2024.11.0"

# Automatically create a skills configuration dictionary from the skills module.
# This allows the skills to be easily imported and used in the brain module.
skills_dict = {
    attr.upper(): getattr(skills, attr)
    for attr in dir(skills)
    if callable(getattr(skills, attr)) and attr.endswith("skill")
}
