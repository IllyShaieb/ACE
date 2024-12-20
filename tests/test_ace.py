import re
import unittest

from ace import __version__


class TestVersion(unittest.TestCase):

    def test_version_format(self):
        """Test that the __version__ attribute follows the correct format."""
        pattern = r"^\d{4}\.\d{2}\.\d+$"  # YYYY.MM.patch format
        self.assertTrue(re.match(pattern, __version__))


if __name__ == "__main__":
    unittest.main()
