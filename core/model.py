"""model.py: Contains the core model for the ACE program."""

from typing import List
import json

import spacy
from spacy.matcher import Matcher


class ACEModel:
    """The main model for the ACE program.

    This class is responsible for processing user input, identifying intents,
    and returning appropriate actions based on the input.
    """

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = Matcher(self.nlp.vocab)
        self._define_intents()

    def __call__(self, user_input: str) -> List[str]:
        """Processes the user's input and returns a list of actions.

        ### Args
            user_input (str): The user's input to process.

        ### Returns
            List[str]: A list of actions based on the input.
        """
        doc = self.nlp(user_input)
        matches = self.matcher(doc)

        if not matches:
            return []

        # Collect all found actions with their priority and start position
        # Result format: (action, priority, start_position)
        intent_map = {intent["name"]: intent for intent in self.intents}
        found_actions = [
            (
                intent_map[self.nlp.vocab.strings[match_id]]["action"],
                intent_map[self.nlp.vocab.strings[match_id]]["priority"],
                start,
            )
            for match_id, start, _ in matches
        ]

        # If there are actions with priority > 1, filter out priority 1 actions
        if any(priority > 1 for _, priority, _ in found_actions):
            found_actions = [
                (action, priority, start)
                for action, priority, start in found_actions
                if priority > 1
            ]

        # Sort actions by start position
        found_actions.sort(key=lambda x: x[2])

        # Return unique actions while preserving order
        return list(dict.fromkeys(action for action, _, _ in found_actions))

    def _define_intents(self):
        """Loads intent definitions from a JSON file and adds them to the matcher."""
        intents_file_path = "data/intents.json"
        try:
            with open(intents_file_path, "r") as f:
                self.intents = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading intents file: {e}")
            self.intents = []

        # Add patterns to the matcher
        for intent in self.intents:
            self.matcher.add(intent["name"], intent["patterns"])
