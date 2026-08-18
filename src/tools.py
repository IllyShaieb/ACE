"""Tools are a functionality that can be used by the agent to perform specific tasks."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Tool(Protocol):
    """A tool allows the agent to perform specific tasks."""

    name: str
    description: str
    parameters: dict[str, Any]

    def execute(self, *args: Any, **kwargs: Any) -> Any: ...

    def to_groq_spec(self) -> dict[str, Any]: ...
