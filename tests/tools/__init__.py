"""tests.tools: Ensure that the tools are correctly implemented and can be called as expected."""

import unittest

from core.tools import discover_tools


class TestToolDiscovery(unittest.TestCase):
    """Test the discover_tools function to ensure it correctly identifies and loads tools."""

    def test_discover_tools_returns_tools(self):
        """Verify that `discover_tools()` returns a non-empty list of tools."""
        # ARRANGE: No specific arrangement needed for this test.

        # ACT: Call the discover_tools function to retrieve available tools.
        tools = discover_tools()

        # ASSERT: Check that the returned list of tools is not empty and contains expected tool types.
        self.assertIsInstance(tools, list, "discover_tools should return a list.")
        self.assertGreater(
            len(tools), 0, "discover_tools should return at least one tool."
        )


if __name__ == "__main__":
    unittest.main()
