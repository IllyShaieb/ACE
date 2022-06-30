import re


class IntentModel:
    """
    A model that predicts the intent of the given text.
    """

    def __init__(self) -> None:
        self.intents = self._load_intents()

    def predict(self, text: str) -> str:
        """
        Predict the intent of the given text.

        returns: The predicted intent, or "unknown" if the intent is unknown.
        """
        return next(
            (
                intent
                for intent, pattern in self.intents.items()
                if self._is_match(text, pattern)
            ),
            "unknown",
        )

    def _is_match(self, text: str, patterns: str) -> bool:
        """
        Helper function to check if the given text matches the given pattern.

        returns: True if the text matches the pattern, False otherwise.
        """
        return bool(re.match("|".join(patterns), text or "", re.IGNORECASE))

    def _load_intents(self) -> dict[str, list]:
        """
        Helper function to create the intents dictionary.

        returns: A dictionary of intents and their patterns.
        """
        return {
            "greeting": ["hello", "hi", "hey", "hi there"],
            "goodbye": ["goodbye", "good bye", "bye"],
            "open_app": ["open", "start"],
            "close_app": ["close", "stop"],
            "show_to_do_list": [
                "what is on my to do list",
                "show my to do list",
                "show my to-do list",
                "show to-do list",
                "get to do list",
                "get to-do list",
                "get my to do list",
            ],
        }
