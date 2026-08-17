"""Tools are a functionality that can be used by the agent to perform specific tasks."""

from datetime import datetime
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Tool(Protocol):
    """A tool allows the agent to perform specific tasks."""

    name: str
    description: str
    parameters: dict[str, Any]

    def execute(self, *args: Any, **kwargs: Any) -> Any: ...

    def to_groq_spec(self) -> dict[str, Any]: ...


class ClockTool:
    """A tool that provides the current time in ISO format."""

    name = "clock"
    description = "Provides the current time in ISO format."
    parameters = {}

    def execute(self) -> str:
        """Return the current time as a string."""
        return datetime.now().isoformat()

    def to_groq_spec(self) -> dict[str, Any]:
        """Return a specification of the tool for use in Groq."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
            "required": [],
        }
