"""core.registry: Contains the registry for tool handlers in the ACE program and the
functionality to register new tools.
"""

import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, Dict

from core.constants import TOOL_NOT_FOUND_MESSAGE


@dataclass
class ToolHandler:
    """Class representing a tool handler.

    This class encapsulates the tool function to be executed, along with metadata
    about whether the tool requires user input and a description of the tool.

    This allows for easy management and invocation of different tools within the ACE
    application.

    Call the tool handler instance to execute the underlying tool function:
    ```python
    result = tool_handler_instance(*args, **kwargs)
    ```

    """

    function: Callable[..., str]
    """Callable[..., str]: The function that implements the tool's functionality."""

    description: str
    """str: A brief description of the tool's purpose and functionality."""

    requires_user_input: bool = field(default=False)
    """bool: Indicates whether the tool requires user input to function."""

    def __call__(self, **kwargs) -> Any:
        """Invoke the tool function using the stored function reference and
        automatically handle any required user input.

        Args:
            **kwargs: Keyword arguments to pass to the tool

        Returns:
            Any: The result of the tool function execution.
        """
        return self.function(**kwargs)


def register_tool(
    name: str,
    registry: Dict[str, ToolHandler],
    requires_user_input: bool = False,
    description: str = "",
) -> Callable[[Callable[..., str]], Callable[..., str]]:
    """Decorator to register a tool handler in the specified registry.

    This decorator wraps a function and registers it as a tool handler with
    the specified name, user input requirement, and description.

    Args:
        name (str): The name of the tool to register.
        registry (dict[str, ToolHandler]): The registry to add the tool handler to.
        requires_user_input (bool): Whether the tool requires user input.
        description (str): A brief description of the tool.

    Returns:
        Callable[[Callable[..., str]], Callable[..., str]]: The decorated function.
    """

    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        if name in registry:
            warnings.warn(
                f"Tool '{name}' is already registered. Overwriting the existing tool handler.",
                UserWarning,
            )

        tool_handler = ToolHandler(
            function=func,
            description=description,
            requires_user_input=requires_user_input,
        )
        registry[name] = tool_handler

        return func

    return decorator


def execute_tool(name: str, registry: dict[str, ToolHandler], **kwargs) -> str:
    """Execute a registered tool by its name with the provided arguments.

    Args:
        name (str): The name of the tool to execute.
        registry (Dict[str, ToolHandler]): The registry to look up the tool handler.
        **kwargs: Keyword arguments to pass to the tool

    Returns:
        str: The result of the tool execution.
    """
    tool_handler = registry.get(name)
    return tool_handler(**kwargs) if tool_handler else TOOL_NOT_FOUND_MESSAGE
