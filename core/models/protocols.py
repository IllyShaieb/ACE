"""core.models.protocols: Protocol definitions for the model components of ACE, specifying the expected
interfaces for data management and business logic."""

from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class ModelProtocol(Protocol):
    """Protocol for the model component, defining the expected interface for data
    management and business logic."""

    async def process_query(self, query: str) -> str:
        """Process a user query asynchronously and return a response."""
        ...

    def load_session(self, session_id: Optional[str] = None) -> None:
        """Load a conversation session by ID, or start a new session if no ID is provided."""
        ...
