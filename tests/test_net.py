import pytest
from ace.net import IntentModel


class TestIntentModel:
    model = IntentModel()

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("", "unknown"),
            (None, "unknown"),
        ],
    )
    def test_predict_unknown(self, text, expected):
        assert self.model.predict(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Hello", "greeting"),
            ("hello", "greeting"),
            ("Hi", "greeting"),
            ("Hey", "greeting"),
            ("hey", "greeting"),
            ("Hello There!", "greeting"),
            ("hello there!", "greeting"),
        ],
    )
    def test_predict_greeting(self, text, expected):
        assert self.model.predict(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Goodbye", "goodbye"),
            ("goodbye", "goodbye"),
            ("Good bye", "goodbye"),
            ("good bye", "goodbye"),
            ("Bye!", "goodbye"),
        ],
    )
    def test_predict_goodbye(self, text, expected):
        assert self.model.predict(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Open word", "open_app"),
            ("open excel", "open_app"),
            ("start Spotify", "open_app"),
        ],
    )
    def test_predict_open_app(self, text, expected):
        assert self.model.predict(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Close word", "close_app"),
            ("close excel", "close_app"),
            ("stop Spotify", "close_app"),
        ],
    )
    def test_predict_close_app(self, text, expected):
        assert self.model.predict(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("What is on my to do list?", "show_to_do_list"),
            ("show my to do list", "show_to_do_list"),
            ("get to do list", "show_to_do_list"),
            ("show to-do list", "show_to_do_list"),
            ("get my to do list", "show_to_do_list"),
        ],
    )
    def test_predict_show_to_do_list(self, text, expected):
        assert self.model.predict(text) == expected
