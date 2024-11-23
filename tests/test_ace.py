"""
This module contains unit tests for the `ace` package.

It currently includes tests for the `__version__` attribute to ensure
that it follows the correct format (YYYY.MM.PATCH).
"""

import re
import unittest

from ace import __version__, disable_logging

disable_logging("ERROR")


class TestVersion(unittest.TestCase):

    def test_version_format(self):
        """Test that the `__version__` attribute follows the correct format.

        This test checks that the `__version__` attribute is a string in the
        format `YYYY.MM.PATCH`, where `YYYY` is the year, `MM` is the month,
        and `PATCH` is the patch version number. The version number must be a
        positive integer.

        TODO: Update the test to check the year and month values follow the
        correct range (e.g., the year is more than the original release year,
        and the month is between 1 and 12).
        """
        pattern = r"^\d{4}\.\d{2}\.\d+$"  # YYYY.MM.patch format
        self.assertTrue(re.match(pattern, __version__))


if __name__ == "__main__":
    unittest.main()
