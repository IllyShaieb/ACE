"""
This module defines configuration settings for the ACE digital assistant.

It currently contains the `INTENT_PATTERNS` dictionary, which maps intent names to
lists of regular expressions used for intent recognition and entity extraction.

The keys in `INTENT_PATTERNS` represent the names of the intents, for example,
"GET_WEATHER_SKILL" or "TELL_TIME_SKILL". The values are lists of regular expressions
that match user input corresponding to that intent.

Each regular expression can contain named capture groups, which are used to extract
entities from the user input. Named capture groups are defined using the syntax
`(?P<group_name>pattern)`, where `group_name` is the name of the entity and `pattern`
is the regular expression to match the entity's value.

Example:

  INTENT_PATTERNS = {
      "DUMMY_SKILL": [
          r"run dummy skill with (?P<group1>.*) and (?P<group2>.*)",
          r"run dummy skill with (?P<group1>.*)",
           "run dummy skill",
      ]
  }

This module also contains configuration settings for the logger and methods to
configure the logger with the specified logging level and handlers.
"""

import logging
import os
from datetime import datetime

LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}
LOG_PATH = f"logs/ace_{datetime.now().strftime('%Y-%m-%d')}.log"
UNIT_TEST_LOG_PATH = f"tests/logs/ace_{datetime.now().strftime('%Y-%m-%d')}.log"
FILE_LOG_FORMATTER = logging.Formatter(
    "{asctime} | {name:<15} | {levelname:<8} | {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
)
CONSOLE_LOG_FORMATTER = logging.Formatter(
    "ACE: {message}", style="{", datefmt="%H:%M:%S"
)
ACE_LOGGING_LEVEL = os.getenv("ACE_LOGGING_LEVEL", "INFO")

INTENT_PATTERNS = {
    "DUMMY_SKILL": [
        r"run dummy skill with (?P<group1>.*) and (?P<group2>.*)",
        r"run dummy skill with (?P<group1>.*)",
        "run dummy skill",
    ],
    "GREETING_SKILL": [r"^(hi|hello|hey)", r"good (morning|afternoon|evening)"],
    "FAREWELL_SKILL": [r"goodbye", r"bye"],
    "WHO_ARE_YOU_SKILL": [r"(who|what) (are) (you)"],
    "HOW_ARE_YOU_SKILL": [r"(how) (are) (you)"],
    "GET_WEATHER_SKILL": [
        r"(?P<timeframe>current) weather in (?P<location>.*)",
        r"weather (?P<timeframe>today) in (?P<location>.*)",
        r"(?P<timeframe>current) weather at (?P<location>.*)",
        r"weather (?P<timeframe>today) at (?P<location>.*)",
        r"weather in (?P<location>.*) (?P<timeframe>today)",
        r"weather (?P<timeframe>tomorrow) in (?P<location>.*)",
        r"weather (?P<timeframe>tomorrow) at (?P<location>.*)",
        r"(?P<timeframe>tomorrow)'s weather in (?P<location>.*)",
        r"(?P<timeframe>tomorrow)'s weather at (?P<location>.*)",
        r"(?P<timeframe>tomorrow)'s weather",
        r"weather (?P<timeframe>tomorrow)",
        r"(?P<timeframe>current) weather",
        r"weather (?P<timeframe>today)",
    ],
    "TELL_TIME_SKILL": [
        r"what is the time",
        r"what time is it",
        r"tell me the time",
        r"current time",
        r"time (?:.*) in (?P<timevalue>.*) (?P<timeunit>hour|minute|second)",
        r"time in (?P<timevalue>.*) (?P<timeunit>hour|minute|second)",
        r"time now",
    ],
    "TODO_SKILL": [
        r"^(?:todo|task|to-do|to do)s? list",
        r"^(?:todo|task|to-do|to do)s$",
        r"^(?P<action>show|give) (?:todo|task|to-do|to do)s?",
        r"^(?P<action>show|give) me my (?:todo|task|to-do|to do)s?",
        r"^(?P<action>show|give) my (?:todo|task|to-do|to do)s?",
        r"^(?P<action>what)(?:'s| is) on my (?:todo|task|to-do|to do)s?",
        r"^(?P<action>what) do I have to do",
        r"^(?P<action>what) are my (?:tasks|todos|to-dos|to dos)",
        r"^(?P<action>add) a task to my (?:todo|task|to-do|to do)s?",
        r"^(?P<action>add) (?P<task>.*) to my (?:todo|task|to-do|to do)s?",
        r"^(?P<action>add) (?:todo|task|to-do|to do)",
    ],
    "NEWS_SKILL": [
        r"(?:show|get) me the news about (?P<topic>.*)?",
        r"(?:show|get) me news about (?P<topic>.*)?",
        r"(?:show|get) news about (?P<topic>.*)?",
        r"(?:show|get) the news about (?P<topic>.*)?",
        r"(?:what is|what's) in the news about (?P<topic>.*)?",
        r"(?:what is|what's) in the news",
        r"(?:what's|what is) the news about (?P<topic>.*)? today",
        r"(?:what's|what is) the news today",
        r"(?:show|get) me the news",
        r"(?:show|get) the news",
        r"(?:show|get) news",
    ],
}
