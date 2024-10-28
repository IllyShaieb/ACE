import unittest
from unittest.mock import patch

from ace.brain import get_user_input


class TestGetInput(unittest.TestCase):
    def test_get_user_input(self):
        with patch("builtins.input", return_value="This is a dummy user input."):
            assert get_user_input() == "This is a dummy user input."
