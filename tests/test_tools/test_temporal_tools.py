"""tests.test_tools.test_temporal_tools: This module contains tests to verify the correct registration
and functionality of temporal-related tool handlers in the ACE application."""

import unittest
from unittest import mock

from core.tools import TOOL_HANDLERS, execute_tool


@mock.patch("core.tools.temporal.datetime")
class TestGetTime(unittest.TestCase):
    """Ensure the GET_TIME tool is registered and functions correctly."""

    def test_get_time_registration(self, mock_datetime):
        """Test that the GET_TIME tool is registered correctly."""

        # ARRANGE
        tool_name = "GET_TIME"
        expected_description = "Provides the current time in a specified timezone."

        # ACT
        tool_handler = TOOL_HANDLERS.get(tool_name)

        # ASSERT
        self.assertIsNotNone(
            tool_handler,
            f"The tool '{tool_name}' should be registered in TOOL_HANDLERS.",
        )

        if tool_handler:
            self.assertEqual(
                tool_handler.description,
                expected_description,
                f"The description of the tool '{tool_name}' should be '{expected_description}'.",
            )

    def test_get_time_execution(self, mock_datetime):
        """Test that the GET_TIME tool returns the current time in the specified timezone."""

        # ARRANGE
        tool_name = "GET_TIME"
        timezone = "GMT"

        # Mock datetime to return a fixed time
        fixed_time = mock.Mock()
        fixed_time.strftime.return_value = "12:00"
        mock_datetime.now.return_value = fixed_time

        # ACT
        result = execute_tool(name=tool_name, registry=TOOL_HANDLERS, timezone=timezone)

        # ASSERT
        self.assertIn(
            "12:00",
            result,
            f"The output of the tool '{tool_name}' should contain the mocked time '12:00'.",
        )


@mock.patch("core.tools.temporal.datetime")
class TestGetDate(unittest.TestCase):
    """Ensure the GET_DATE tool is registered and functions correctly."""

    def test_get_date_registration(self, mock_datetime):
        """Test that the GET_DATE tool is registered correctly."""

        # ARRANGE
        tool_name = "GET_DATE"
        expected_description = "Provides the current date in a human-readable format."

        # ACT
        tool_handler = TOOL_HANDLERS.get(tool_name)

        # ASSERT
        self.assertIsNotNone(
            tool_handler,
            f"The tool '{tool_name}' should be registered in TOOL_HANDLERS.",
        )

        if tool_handler:
            self.assertEqual(
                tool_handler.description,
                expected_description,
                f"The description of the tool '{tool_name}' should be '{expected_description}'.",
            )

    def test_get_date_execution(self, mock_datetime):
        """Test that the GET_DATE tool returns the current date in a human-readable format."""

        # ARRANGE
        tool_name = "GET_DATE"
        expected_date_components = [
            "Thursday",
            "20th",
            "November",
            "2025",
        ]

        # Mock datetime to return a fixed date
        fixed_date = mock.Mock()
        fixed_date.day = 20
        fixed_date.strftime.side_effect = lambda fmt: {
            "%A": "Thursday",
            "%d": "20th",
            "%B %Y": "November 2025",
        }[fmt]
        mock_datetime.now.return_value = fixed_date

        # ACT
        result = execute_tool(name=tool_name, registry=TOOL_HANDLERS)

        # ASSERT
        for component in expected_date_components:
            self.assertIn(
                component,
                result,
                f"The output of the tool '{tool_name}' should contain the date component '{component}'.",
            )


if __name__ == "__main__":
    unittest.main()
