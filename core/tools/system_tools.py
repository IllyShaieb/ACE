"""core.tools.system_tools: This module provides the tools for retrieving system and identity
information"""

from core.tools import TOOL_HANDLERS, register_tool


@register_tool(
    name="SELF_NAME",
    description="Returns the name of the ACE application.",
    registry=TOOL_HANDLERS,
)
def self_name() -> str:
    """Returns the name of the ACE application.

    Returns:
        str: A string representing the name of the ACE application.
    """
    return "My name is ACE, the Artificial Consciousness Engine."


@register_tool(
    name="SELF_CREATOR",
    description="Provides information about the assistant's creator.",
    registry=TOOL_HANDLERS,
)
def self_creator() -> str:
    """Returns the name of the creator."""
    return "My development was overseen by Illy Shaieb."
