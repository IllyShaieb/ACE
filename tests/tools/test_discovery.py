"""tests.tools.test_discovery: Tests for dynamic tool discovery."""

import unittest

from core.tools import discover_tools


class TestToolDiscovery(unittest.TestCase):
    """Test discover_tools to ensure it identifies and loads tools."""

    def test_discover_tools_returns_tools(self):
        """Verify that discover_tools() returns a non-empty list of tools."""
        # ACT: Call the discover_tools function to retrieve available tools.
        tools = discover_tools()

        # ASSERT: Check that the returned list is not empty.
        self.assertIsInstance(tools, list, "discover_tools should return a list.")
        self.assertGreater(
            len(tools), 0, "discover_tools should return at least one tool."
        )


if __name__ == "__main__":
    unittest.main()
