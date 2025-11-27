"""tests.test_tools.test_registry.py: This module contains tests to verify the correct registration
and functionality of tool handlers within the ACE application. This ensures that each tool
can be invoked correctly and behaves as expected.
"""

import unittest

from core.constants import TOOL_NOT_FOUND_MESSAGE
from core.tools import ToolHandler, execute_tool, register_tool


class TestToolHandler(unittest.TestCase):
    """Ensures the ToolHandler class correctly encapsulates the tool and allows the
    tool to be called with any arguments.
    """

    def test_tool_handler_initialisation(self):
        """Test that ToolHandler initialises correctly."""

        # ARRANGE
        def sample_tool(x):
            return x * 2

        tool_handler = ToolHandler(
            function=sample_tool,
            description="A sample tool that doubles the input.",
            requires_user_input=True,
        )
        x = 3
        expected_result = 6

        # ACT
        function = tool_handler.function
        requires_input = tool_handler.requires_user_input
        description = tool_handler.description

        # ASSERT
        self.assertEqual(
            function(x=x),
            expected_result,
            "The registered function should match the output of the sample tool.",
        )
        self.assertTrue(
            requires_input,
            "The tool handler should indicate that user input is required.",
        )
        self.assertEqual(
            description,
            "A sample tool that doubles the input.",
            "The description should match the provided description.",
        )

    def test_tool_handler_call(self):
        """Test that calling the ToolHandler invokes the underlying function."""

        # ARRANGE
        def sample_tool(x, y):
            return x + y

        tool_handler = ToolHandler(
            function=sample_tool,
            description="A sample tool that adds two numbers.",
            requires_user_input=False,
        )

        x, y = 5, 7
        expected_result = 12

        # ACT
        result = tool_handler(x=x, y=y)

        # ASSERT
        self.assertEqual(
            result,
            expected_result,
            "Calling the ToolHandler should return the sum of the two inputs.",
        )


class TestRegisterToolDecorator(unittest.TestCase):
    """Verifies that the register_tool decorator correctly adds a function to the tool registry
    with the appropriate metadata.
    """

    MOCK_REGISTRY = {}

    def test_register_tool_decorator(self):
        """Test that the register_tool decorator registers a tool correctly."""

        # ARRANGE
        @register_tool(
            name="mock_tool",
            description="A mock tool for testing.",
            requires_user_input=True,
            registry=self.MOCK_REGISTRY,
        )
        def mock_tool_function(a, b):
            return a * b

        a, b = 4, 5

        # ACT
        tool_handler = self.MOCK_REGISTRY.get("mock_tool")
        result = tool_handler(a=a, b=b) if tool_handler else None
        mocked_tool_result = mock_tool_function(a=a, b=b)

        # ASSERT
        self.assertIsNotNone(
            tool_handler,
            "The tool handler should be registered in the mock registry.",
        )
        self.assertEqual(
            result,
            mocked_tool_result,
            "The registered tool function should return the expected result when called.",
        )

    def test_register_tool_overwrite_warning(self):
        """Test that registering a tool with an existing name raises a warning."""

        # ARRANGE
        @register_tool(
            name="duplicate_tool",
            requires_user_input=False,
            description="First registration of duplicate tool.",
            registry=self.MOCK_REGISTRY,
        )
        def first_tool():
            return "First"

        # ASSERT
        with self.assertWarns(
            UserWarning,
            msg="Registering a tool with an existing name should raise a warning.",
        ):

            # ACT
            @register_tool(
                name="duplicate_tool",
                requires_user_input=True,
                description="Second registration of duplicate tool.",
                registry=self.MOCK_REGISTRY,
            )
            def second_tool():
                return "Second"


class TestExecuteToolFunction(unittest.TestCase):
    """Tests that the execute_tool function correctly invokes registered tools and handles
    errors.
    """

    MOCK_REGISTRY = {}

    def setUp(self):
        """Set up a mock registry with sample tools for testing."""

        @register_tool(
            name="add_tool",
            description="Adds two numbers.",
            requires_user_input=False,
            registry=self.MOCK_REGISTRY,
        )
        def add_tool(x, y):
            return x + y

        @register_tool(
            name="error_tool",
            description="A tool that raises an error.",
            requires_user_input=False,
            registry=self.MOCK_REGISTRY,
        )
        def error_tool():
            raise ValueError("Intentional error for testing.")

    def test_execute_tool_success(self):
        """Test that execute_tool successfully invokes a registered tool."""

        # ARRANGE
        tool_name = "add_tool"
        x, y = 10, 15
        expected_result = 25

        # ACT
        result = execute_tool(
            tool_name,
            registry=self.MOCK_REGISTRY,
            x=x,
            y=y,
        )

        # ASSERT
        self.assertEqual(
            result,
            expected_result,
            "The execute_tool function should return the correct result from the add_tool.",
        )

    def test_execute_tool_not_found(self):
        """Test that execute_tool handles the case where the tool is not found."""

        # ARRANGE
        tool_name = "non_existent_tool"

        # ACT
        result = execute_tool(
            tool_name,
            registry=self.MOCK_REGISTRY,
        )

        # ASSERT
        self.assertEqual(
            result,
            TOOL_NOT_FOUND_MESSAGE,
            "The execute_tool function should return the TOOL_NOT_FOUND_MESSAGE when the tool is not found.",
        )


if __name__ == "__main__":
    unittest.main()
