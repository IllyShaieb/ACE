"""tests.test_tools.test_identity_tools: This module contains tests to verify the correct registration
and functionality of identity-related tool handlers in the ACE application."""

import unittest

from core.tools import TOOL_HANDLERS, execute_tool


class TestSelfName(unittest.TestCase):
    """Ensure the SELF_NAME tool is registered and functions correctly."""

    def test_self_name_registration(self):
        """Test that the SELF_NAME tool is registered correctly."""

        # ARRANGE
        tool_name = "SELF_NAME"
        expected_description = "Returns the name of the ACE application."

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

    def test_self_name_execution(self):
        """Test that the SELF_NAME tool executes correctly."""

        # ARRANGE
        tool_name = "SELF_NAME"
        expected_output_components = ["ACE", "Artificial Consciousness Engine"]

        # ACT
        result = execute_tool(name=tool_name, registry=TOOL_HANDLERS)

        # ASSERT
        for component in expected_output_components:
            self.assertIn(
                component,
                result,
                f"The output of the tool '{tool_name}' should contain '{component}'.",
            )


class TestSelfCreator(unittest.TestCase):
    """Ensure the SELF_CREATOR tool is registered and functions correctly."""

    def test_self_creator_registration(self):
        """Test that the SELF_CREATOR tool is registered correctly."""

        # ARRANGE
        tool_name = "SELF_CREATOR"
        expected_description = "Provides information about the assistant's creator."

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

    def test_self_creator_execution(self):
        """Test that the SELF_CREATOR tool executes correctly."""

        # ARRANGE
        tool_name = "SELF_CREATOR"
        expected_output = "Illy Shaieb"

        # ACT
        result = execute_tool(name=tool_name, registry=TOOL_HANDLERS)

        # ASSERT
        self.assertIn(
            expected_output,
            result,
            f"The output of the tool '{tool_name}' should contain '{expected_output}'.",
        )


if __name__ == "__main__":
    unittest.main()
