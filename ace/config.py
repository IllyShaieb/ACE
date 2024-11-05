INTENT_PATTERNS = {
    "DUMMY_SKILL": [
        r"run dummy skill with (\d+) and (\d+)",
        r"run dummy skill with (\d+)",
        "run dummy skill",
    ],
    "GREETING_SKILL": [r"(hi|hello|hey)", r"good (morning|afternoon|evening)"],
    "FAREWELL_SKILL": [r"goodbye", r"bye"],
    "WHO_ARE_YOU_SKILL": [r"(who|what) (are) (you)"],
    "HOW_ARE_YOU_SKILL": [r"(how) (are) (you)"],
}
