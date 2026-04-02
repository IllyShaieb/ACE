"""core.tools.protocols: Protocol definitions for the tool components of ACE, specifying the expected
interfaces for functional tools that ACE can use."""

from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class ToolProtocol(Protocol):
    """Protocol for tools, defining the expected interface for functional tools that
    ACE can use."""

    @property
    def name(self) -> str:
        """Return the name of the tool."""
        ...

    @property
    def description(self) -> str:
        """Return a brief description of the tool's functionality."""
        ...

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return a schema defining the parameters required by the tool."""
        ...

    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool's functionality with the given parameters."""
        ...
