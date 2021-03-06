import pytest
from ace.outputs import CommandLineOutput
from ace.utils import TextProcessor

text_processor = TextProcessor()


class TestCommandLineOutput:
    @pytest.mark.parametrize(
        "prefix,message,expected",
        [
            ("", "Hello", "Hello\n"),
            (None, "Hello", "Hello\n"),
            ("", "", "\n"),
            ("  ", "Spaces are trimmed", "Spaces are trimmed\n"),
        ],
    )
    def test_broadcast_command_line_output_no_prefix(
        self, prefix, message, expected, capsys
    ):
        text_output = CommandLineOutput(prefix)
        text_output.broadcast(message)

        assert text_processor.remove_ansi_escape(capsys.readouterr().out) == expected

    @pytest.mark.parametrize(
        "prefix,message,expected",
        [
            ("1", "Hello", "1 Hello\n"),
            ("2    ", "I'm trimmed", "2 I'm trimmed\n"),
            ("Hello ", "World", "Hello World\n"),
        ],
    )
    def test_broadcast_command_line_output_no_special_character(
        self, prefix, message, expected, capsys
    ):
        text_output = CommandLineOutput(prefix)
        text_output.broadcast(message)

        assert text_processor.remove_ansi_escape(capsys.readouterr().out) == expected

    @pytest.mark.parametrize(
        "prefix,message,expected",
        [
            ("ACE:", "Hello", "ACE: Hello\n"),
            (">", "Hello world!", "> Hello world!\n"),
            ("-     ", "Spam", "- Spam\n"),
        ],
    )
    def test_broadcast_command_line_output_special_character(
        self, prefix, message, expected, capsys
    ):
        text_output = CommandLineOutput(prefix)
        text_output.broadcast(message)

        assert text_processor.remove_ansi_escape(capsys.readouterr().out) == expected
