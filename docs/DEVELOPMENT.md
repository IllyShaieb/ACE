# Development Guidelines

## Overview

This section provides guidelines and best practices for developing new features, tools, and components within the ACE framework. It covers the process of adding new tools, ensuring they are properly structured, and testing their functionality to maintain the integrity and reliability of the ACE ecosystem.

## Core Principles
ACE is built on a structured folder hierachy that organises its components into logical sections. The foundation of ACE is the Model-View-Controller (MVC) architecture, which separates the application into three interconnected components:
- **Model**: Manages the core logic and state of the application.
- **View**: Handles the presentation layer and user interface.
- **Controller**: Acts as an intermediary between the Model and View, processing user input and updating the Model and View accordingly.

This is supported by specialised infrastructure layers:
- **Adapters**: Facilitate communication between ACE and external systems, such as APIs or databases.
- **Services**: Orchestrate adapters to perform specific tasks.
- **Tools**: Provide reusable functionalities that can be invoked by the Model to perform specific actions.

## Tool Auto-Discovery
ACE automatically discovers and registers tools defined in the `tools` module. To create a new tool, simply define a class that follows the required structure, and it will be available for use without any additional registration steps.

### Step 1: Add a New Tool
To add new tools, either create a new file in the `tools` directory or add a new class to an existing file. The auto-discovery mechanism will ensure that your tool is registered and ready to use.

A tool class must have the following attributes and methods:
- `name`: A string property that returns the name of the tool.
- `description`: A string property that provides a description of what the tool does.
- `parameters_schema`: A property that returns a JSON schema describing the parameters the tool accepts.
- `execute(**kwargs)`: A method that performs the tool's action and returns its result. The parameters for this method should match the schema defined in `parameters_schema`.

```python
class ExampleTool:
    @property
    def name(self) -> str:
        return "example_tool"

    @property
    def description(self) -> str:
        return "This is an example tool that demonstrates the required structure."

    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "OBJECT",
            "properties": {
                "param1": {"type": "STRING", "description": "A string parameter."},
                "param2": {"type": "INTEGER", "description": "An integer parameter."},
            },
            "required": ["param1", "param2"],
        }

    def execute(self, param1: str, param2: int, **kwargs) -> str:
        """Example execution method that returns a formatted string."""
        return f"Received param1: {param1} and param2: {param2}"
```

### Step 2: Testing Your Tool
Once a tool has been defined you must ensure it has associated tests to validate its functionality. Tests should be placed in the `tests\tools` directory and follow the naming convention `test_<tool_name>.py`. Each test file should contain test cases that cover various scenarios for the tool's execution, including edge cases and error handling.

```python
import unittest
from core.tools.example_tool import ExampleTool

class TestExampleTool(unittest.TestCase):
    """Tests for the ExampleTool."""

    def setUp(self):
        self.tool = ExampleTool()

    def test_example_tool_execution(self):
        """Test the execution of the ExampleTool."""
        result = self.tool.execute(param1="test", param2=123)
        expected = "Received param1: test and param2: 123"
        self.assertEqual(result, expected)

    def test_example_tool_missing_parameters(self):
        """Test execution with missing parameters."""
        with self.assertRaises(TypeError):
            self.tool.execute(param1="test")  # Missing param2
```