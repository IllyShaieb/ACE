"""Tools are a functionality that can be used by the agent to perform specific tasks."""

import os
from datetime import datetime
from typing import Any, Protocol, runtime_checkable

import requests
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()


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


class WolframAlphaTool:
    """A tool that queries Wolfram Alpha for answers."""

    name = "wolfram_alpha"
    description = (
        "Compute and look up exact mathematical, scientific, physical, or factual knowledge. "
        "Use this tool for mathematical calculations (algebra, calculus, arithmetic), "
        "unit and currency conversions, physical constants, chemistry/physics properties, "
        "astronomical data, and demographic statistics."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The exact computational or factual query to calculate.",
            }
        },
        "required": ["query"],
    }

    def execute(self, query: str) -> str:
        """Execute the tool with the given query.

        Args:
            query (str): The query to send to Wolfram Alpha.

        Returns:
            str: The response from Wolfram Alpha as a JSON-formatted string.
        """
        # Make a request to the Wolfram Alpha API
        data = requests.get(
            "https://api.wolframalpha.com/v2/query",
            params={
                "input": query,
                "appid": os.getenv("WOLFRAM_ALPHA_APP_ID"),
                "output": "JSON",
            },
        ).json()

        # If the query was not successful, return an error message
        query_result = data.get("queryresult", {})
        if not query_result.get("success"):
            return "Wolfram Alpha was unable to calculate a result for this query."

        # Extract human-readable text lines from Wolfram's pods
        lines = []
        for pod in query_result.get("pods", []):
            title = pod.get("title", "")
            for subpod in pod.get("subpods", []):
                text = subpod.get("plaintext", "").strip()
                if text:
                    lines.append(f"{title}: {text}" if title else text)

        return "\n".join(lines) if lines else "No text result returned."

    def to_groq_spec(self) -> dict[str, Any]:
        """Return a specification of the tool for use in Groq."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
            "required": ["query"],
        }


class DuckDuckGoSearchTool:
    """Tool for searching the web for real-time news, information, and current events."""

    name = "duckduckgo_search"
    description = (
        "Search the web for up-to-date information, current news, public figures, "
        "recent events, and facts beyond training data cutoff. Use this tool whenever "
        "the user asks for recent information or real-time web lookups."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query keywords to look up on the web.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of search results to return (default 5).",
            },
        },
    }

    def execute(self, query: str, max_results: int = 5) -> str:
        """Execute a web search and return formatted titles, URLs, and snippets."""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return "No search results found."

            formatted = []
            for r in results:
                title = r.get("title", "No Title")
                link = r.get("href", "")
                snippet = r.get("body", "")
                formatted.append(f"Title: {title}\nURL: {link}\nSnippet: {snippet}\n")

            return "\n---\n".join(formatted)

        except Exception as e:
            return f"Error executing web search: {str(e)}"

    def to_groq_spec(self) -> dict[str, Any]:
        """Return the Groq/OpenAI tool specification."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
            "required": ["query"],
        }
