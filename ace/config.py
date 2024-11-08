INTENT_PATTERNS = {
    "DUMMY_SKILL": [
        r"run dummy skill with (\d+) and (\d+)",
        r"run dummy skill with (\d+)",
        "run dummy skill",
    ],
    "GREETING_SKILL": [r"^(hi|hello|hey)", r"good (morning|afternoon|evening)"],
    "FAREWELL_SKILL": [r"goodbye", r"bye"],
    "WHO_ARE_YOU_SKILL": [r"(who|what) (are) (you)"],
    "HOW_ARE_YOU_SKILL": [r"(how) (are) (you)"],
    "CURRENT_WEATHER_SKILL": [
        r"current weather in (.*)",
        r"weather today in (.*)",
        r"current weather at (.*)",
        r"weather today at (.*)",
        r"weather in (.*) today",
        r"current weather",
        r"weather today",
    ],
    "FUTURE_WEATHER_SKILL": [
        r"weather tomorrow in (.*)",
        r"weather tomorrow at (.*)",
        r"tomorrow's weather in (.*)",
        r"tomorrow's weather at (.*)",
        r"tomorrow's weather",
        r"weather tomorrow",
    ],
}
