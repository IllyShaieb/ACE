"""tests.tools.test_system: Unit tests for system-level tools to ensure they execute correctly and
return expected results."""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

import pytz

from core.tools import system


class TestClockTool(unittest.TestCase):
    """Test the ClockTool's ability to execute and return the current date and time."""

    def setUp(self):
        """Set up common test components."""
        self.tool = system.ClockTool()

    @patch("time.tzname", ("GMT", "GMT"))
    def test_execute_returns_current_date_time(self):
        """Verify that `execute()` returns a string representing the current date and time."""
        # ARRANGE: Define a fixed datetime for testing
        fixed_datetime = pytz.timezone("GMT").localize(datetime(2026, 1, 1, 12, 0, 0))
        with patch("core.tools.system.datetime") as mock_datetime:
            mock_datetime.now.return_value.astimezone.return_value = fixed_datetime

            # ACT: Execute the tool
            result = self.tool.execute()

            # ASSERT: Verify the result matches the expected string
            self.assertIsInstance(result, str)
            self.assertEqual(result, "2026-01-01T12:00:00 +0000 (GMT)")

    def test_execute_with_format_parameter(self):
        """Verify that `execute()` returns the correct format based on the 'format' parameter."""
        # ARRANGE: Define a fixed datetime for testing
        fixed_datetime = pytz.timezone("GMT").localize(datetime(2026, 1, 1, 12, 0, 0))
        with patch("core.tools.system.datetime") as mock_datetime:
            mock_datetime.now.return_value.astimezone.return_value = fixed_datetime

            # ACT & ASSERT: Test different format options
            self.assertEqual(self.tool.execute(format="time"), "12:00:00 +0000 (GMT)")
            self.assertEqual(self.tool.execute(format="date"), "2026-01-01")
            self.assertEqual(
                self.tool.execute(format="both"), "2026-01-01T12:00:00 +0000 (GMT)"
            )

    def test_execute_with_timezone_parameter(self):
        """Verify that `execute()` can handle the 'timezone' parameter (even if it doesn't change the output)."""
        # ARRANGE: Define a fixed datetime for testing in UTC
        fixed_datetime = pytz.utc.localize(datetime(2026, 1, 1, 4, 0, 0))
        with patch("core.tools.system.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_datetime

            # ACT: Execute the tool with a timezone parameter
            result = self.tool.execute(timezone="Asia/Singapore")

            # ASSERT: Verify the tool returns the date and time converted to the specified timezone (+8 hours for Singapore)
            self.assertIsInstance(result, str)
            self.assertEqual(result, "2026-01-01T12:00:00 +0800 (Asia/Singapore)")


if __name__ == "__main__":
    unittest.main()
