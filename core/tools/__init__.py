"""tools: This module contains various functions that support the core functionality
of ACE.

These utilities allow the model to perform specific tasks, such as web searching,
getting the current time or date, and other utility functions.

Each tool is implemented as a function that can be called with specific parameters
to perform its task.

To add a new tool:
1. Create a new function inside one of these modules if it fits the category or
    create a new module if it doesn't.
2. Decorate the function with the `@register_tool` decorator to register it as a tool.
3. Add corresponding tests for the tool in the tests/ directory.
4. Ensure the function has a clear docstring explaining its purpose and parameters.
"""

from dotenv import load_dotenv

from .registry import ToolHandler, execute_tool, register_tool

TOOL_HANDLERS: dict[str, ToolHandler] = {}
"""A dictionary that maps tool names to their corresponding ToolHandler instances."""

load_dotenv(override=True)

from . import entertainment_tools as entertainment_tools  # noqa: F401, E402
from . import system_tools as identity_tools  # noqa: F401, E402
from . import temporal_tools as temporal_tools  # noqa: F401, E402
from . import web_tools as web_tools  # noqa: F401, E402

__all__ = [
    "TOOL_HANDLERS",
    "ToolHandler",
    "register_tool",
    "execute_tool",
    "entertainment_tools",
    "identity_tools",
    "temporal_tools",
    "web_tools",
]
