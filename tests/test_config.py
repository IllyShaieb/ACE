"""Ensure the configuration functions are working correctly."""

import logging
from pathlib import Path

from src.config import setup_logging


class TestSetupLogging:
    """Test suite for the setup_logging function."""

    def test_writes_records_to_loggers(self, tmp_path, capsys):
        """Ensure that setup_logging writes log records to the specified loggers."""
        # ARRANGE: Prepare a temporary log file path, and a logger
        log_file = Path(tmp_path, "test_log").resolve()

        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)

        # ACT: Set up logging with the temporary log file and log to the handlers
        setup_logging(
            log_file=log_file, console_level=logging.DEBUG, file_level=logging.DEBUG
        )
        logger.debug("This is a test log message.")

        for handler in logging.getLogger().handlers:
            # Flush handlers to guarantee disk and stream output is up-to-date
            handler.flush()

        # ASSERT: Check that the log file was created and contains the expected log message
        log_contents = log_file.read_text()
        console_contents = capsys.readouterr().out

        assert log_file.exists(), f"Expected log file at {log_file} to exist"
        assert (
            "This is a test log message." in log_contents
        ), "Expected log file to contain 'This is a test log message.'"

        assert (
            "This is a test log message." in console_contents
        ), "Expected console output to match captured output"

    def test_setup_logging_respects_different_stream_levels(self, tmp_path, capsys):
        """Ensure that setup_logging respects different logging levels for console and file handlers."""
        # ARRANGE: Prepare a temporary log file path, and a logger
        log_file = Path(tmp_path, "test_log").resolve()

        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)

        # ACT: Set up logging with different levels for console and file handlers
        setup_logging(
            log_file=log_file, console_level=logging.ERROR, file_level=logging.DEBUG
        )
        logger.debug("This is a debug message.")
        logger.error("This is an error message.")

        for handler in logging.getLogger().handlers:
            # Flush handlers to guarantee disk and stream output is up-to-date
            handler.flush()

        # ASSERT: Check that the log file contains both messages, but the console only contains the error message
        log_contents = log_file.read_text()
        console_contents = capsys.readouterr().out

        assert (
            "This is a debug message." in log_contents
        ), "Expected log file to contain the debug message"
        assert (
            "This is an error message." in log_contents
        ), "Expected log file to contain the error message"
        assert (
            "This is an error message." in console_contents
        ), "Expected console output to contain the error message"
        assert (
            "This is a debug message." not in console_contents
        ), "Expected console output to not contain the debug message"

    def test_setup_logging_mutes_external_libraries_below_warning(
        self, tmp_path, capsys
    ):
        """Ensure that setup_logging mutes external libraries below the WARNING level."""
        # ARRANGE: Prepare a temporary log file path, and a logger
        log_file = Path(tmp_path, "test_log").resolve()

        logger = logging.getLogger("httpx")
        logger.setLevel(logging.DEBUG)

        # ACT: Set up logging
        setup_logging(log_file=log_file)
        logger.debug("This is a debug message from httpx.")
        logger.warning("This is a warning message from httpx.")

        for handler in logging.getLogger().handlers:
            # Flush handlers to guarantee disk and stream output is up-to-date
            handler.flush()

        # ASSERT: Check that the debug message is not logged, but the warning message is
        log_contents = log_file.read_text()
        console_contents = capsys.readouterr().out

        assert (
            "This is a debug message from httpx." not in log_contents
        ), "Expected log file to not contain the debug message from httpx"
        assert (
            "This is a warning message from httpx." in log_contents
        ), "Expected log file to contain the warning message from httpx"
        assert (
            "This is a debug message from httpx." not in console_contents
        ), "Expected console output to not contain the debug message from httpx"
        assert (
            "This is a warning message from httpx." in console_contents
        ), "Expected console output to contain the warning message from httpx"

    def test_setup_logging_enables_src_package_debug_tracing(self, tmp_path, capsys):
        """Verify internal src child loggers inherit DEBUG level."""
        # ARRANGE: Prepare a temporary log file path, and a logger
        log_file = Path(tmp_path, "test_log").resolve()

        logger = logging.getLogger("src.child")
        logger.setLevel(logging.DEBUG)

        # ACT: Set up logging
        setup_logging(
            log_file=log_file, console_level=logging.DEBUG, file_level=logging.DEBUG
        )
        logger.debug("This is a debug message from src.child.")

        for handler in logging.getLogger().handlers:
            # Flush handlers to guarantee disk and stream output is up-to-date
            handler.flush()

        # ASSERT: Check that the debug message from the 'src.child' logger is logged
        log_contents = log_file.read_text()
        console_contents = capsys.readouterr().out

        assert (
            "This is a debug message from src.child." in log_contents
        ), "Expected log file to contain the debug message from src.child"
        assert (
            "This is a debug message from src.child." in console_contents
        ), "Expected console output to contain the debug message from src.child"

    def test_setup_logging_records_match_pipe_structure(self, tmp_path, capsys):
        """Verify that log records follow the expected pipe-separated structure."""
        # ARRANGE: Prepare a temporary log file path, and a logger
        log_file = Path(tmp_path, "test_log").resolve()

        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)

        expected_log_format = (
            "{timestamp} | {level} | {source_file} | {function_name} | {message}"
        )
        expected_log_length = len(expected_log_format.split(" | "))

        # ACT: Set up logging
        setup_logging(
            log_file=log_file, console_level=logging.DEBUG, file_level=logging.DEBUG
        )
        logger.debug("This is a test log message.")

        for handler in logging.getLogger().handlers:
            # Flush handlers to guarantee disk and stream output is up-to-date
            handler.flush()

        # ASSERT: Check that the log records follow the expected pipe-separated structure
        log_contents = log_file.read_text()
        console_contents = capsys.readouterr().out

        log_content_lines = log_contents.strip().split("\n")
        console_content_lines = console_contents.strip().split("\n")

        for line in log_content_lines:
            parts = line.split(" | ")
            assert (
                len(parts) >= expected_log_length
            ), f"File Log: Expected log file line to have at least {expected_log_length} pipe-separated parts"
            assert parts[0], "File Log: Expected timestamp to be present"
            assert "DEBUG" in parts[1], "File Log: Expected log level to be DEBUG"
            assert (
                "test_config.py" in parts[2]
            ), "File Log: Expected source file to be test_config.py"
            assert (
                "test_setup_logging_records_match_pipe_structure" in parts[3]
            ), "File Log: Expected function name to be test_setup_logging_records_match_pipe_structure"
            assert (
                "This is a test log message." in parts[4]
            ), "File Log: Expected log message to be 'This is a test log message.'"

        for line in console_content_lines:
            parts = line.split(" | ")
            assert (
                len(parts) >= expected_log_length
            ), f"Console Log: Expected console output line to have at least {expected_log_length} pipe-separated parts"
            assert parts[0], "Console Log: Expected timestamp to be present"
            assert "DEBUG" in parts[1], "Console Log: Expected log level to be DEBUG"
            assert (
                "test_config.py" in parts[2]
            ), "Console Log: Expected source file to be test_config.py"
            assert (
                "test_setup_logging_records_match_pipe_structure" in parts[3]
            ), "Console Log: Expected function name to be test_setup_logging_records_match_pipe_structure"
            assert (
                "This is a test log message." in parts[4]
            ), "Console Log: Expected log message to be 'This is a test log message.'"

    def test_setup_logging_handles_none_levels_gracefully(self, tmp_path):
        """Test that setup_logging does not raise an exception when console_level or file_level is None."""
        # ARRANGE: Create a temporary log file
        log_file = Path(tmp_path, "test_log").resolve()

        # ACT: Call setup_logging with None levels
        setup_logging(log_file=log_file, console_level=None, file_level=None)
        logger = logging.getLogger()
        logger.debug("This is a test log message with None levels.")

        for handler in logger.handlers:
            handler.flush()

        # ASSERT: Check that the log message is written to the log file
        log_contents = log_file.read_text()
        assert "This is a test log message with None levels." in log_contents

    def test_setup_logging_creates_log_file_if_not_exists(self, tmp_path):
        """Test that setup_logging creates the log file if it does not exist."""
        # ARRANGE: Create a temporary log file path
        log_file = Path(tmp_path, "test_log", "log.log").resolve()

        # ACT: Call setup_logging
        setup_logging(log_file=log_file)

        # ASSERT: Check that the log file has been created
        assert (
            log_file.exists()
        ), "Expected the log file to be created if it did not exist."
