"""Tools are a functionality that can be used by the agent to perform specific tasks."""

import logging
import os
import re
from datetime import datetime
from typing import Any, Protocol, runtime_checkable
from urllib.parse import urljoin

import requests
from ddgs import DDGS
from dotenv import load_dotenv
from selectolax.lexbor import LexborHTMLParser as HTMLParser
from selectolax.lexbor import LexborNode as Node

load_dotenv()

logger = logging.getLogger(__name__)


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
        try:
            response = requests.get(
                "https://api.wolframalpha.com/v2/query",
                params={
                    "input": query,
                    "appid": os.getenv("WOLFRAM_ALPHA_APP_ID"),
                    "output": "JSON",
                },
            )
            response.raise_for_status()
            data = response.json()
        except Exception as error:
            logger.warning(
                "wolfram_alpha_failed tool=%s failure_reason=request_error error_type=%s",
                self.name,
                type(error).__name__,
                exc_info=True,
            )
            return f"Error occurred while querying Wolfram Alpha: {str(error)}"

        # If the query was not successful, return an error message
        query_result = data.get("queryresult", {})
        if not query_result.get("success"):
            raw_error = query_result.get("error")

            # Case 1: Wolfram execution or credential error
            if isinstance(raw_error, dict):
                error_status = raw_error.get("status", "unknown")
                logger.warning(
                    "wolfram_alpha_failed tool=%s failure_reason=api_error error_status=%s",
                    self.name,
                    error_status,
                )
                return "Wolfram Alpha returned an API error."

            if isinstance(raw_error, str) and raw_error:
                logger.warning(
                    "wolfram_alpha_failed tool=%s failure_reason=api_error",
                    self.name,
                )
                return "Wolfram Alpha returned an API error."

            # Case 2: Query could not be parsed or computed
            did_you_mean = query_result.get("didyoumeans")
            suggestion = ""
            if isinstance(did_you_mean, dict):
                val = did_you_mean.get("val")
                if val:
                    suggestion = f" Did you mean '{val}'?"
            elif isinstance(did_you_mean, list) and did_you_mean:
                val = did_you_mean[0].get("val")
                if val:
                    suggestion = f" Did you mean '{val}'?"

            logger.warning(
                "wolfram_alpha_failed tool=%s failure_reason=cannot_parse",
                self.name,
            )
            return f"Wolfram Alpha could not understand the query.{suggestion}"

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
            logger.warning(
                "web_search_failed tool=%s error_type=%s",
                self.name,
                type(e).__name__,
                exc_info=True,
            )
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


class UrlReaderTool:
    """Tool for reading the content of a web page given its URL."""

    name = "url_reader"
    description = (
        "Read the content of a web page given its URL. Use this tool to extract text "
        "from web pages for analysis or summarization."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL of the web page to read.",
            },
            "start_character": {
                "type": "integer",
                "description": (
                    "The starting character index from which to return the page content. "
                    "Defaults to 0."
                ),
            },
            "character_length_cap": {
                "type": "integer",
                "description": (
                    "Maximum number of characters to return from the page content. "
                    "Defaults to 8000."
                ),
            },
            "show_urls": {
                "type": "boolean",
                "description": (
                    "Whether to show URLs in the extracted content. Defaults to False."
                ),
            },
        },
        "required": ["url"],
    }

    def _convert_links_to_markdown(
        self, node: Node, base_url: str, show_urls: bool
    ) -> None:
        """Convert internal <a> tags into Markdown formatted text.

        Args:
            node (Node): The HTML node to process.
            base_url (str): The base URL to resolve relative links.
            show_urls (bool): Whether to show URLs in the extracted content.
        """
        for a_tag in node.css("a"):
            # Extract the href attribute and link text, handling cases where they may be missing
            href = (a_tag.attributes.get("href") or "").strip()
            link_text = a_tag.text(strip=True)

            # Ignore empty links or internal jump fragment anchors
            if not href or href.startswith("#") or not link_text:
                continue

            full_url = urljoin(base_url, href)

            # Replace tag with markdown text if show_urls is True
            if show_urls:
                a_tag.replace_with(f" [{link_text}]({full_url}) ")
            else:
                a_tag.replace_with(f" {link_text} ")

    def execute(
        self,
        url: str,
        start_character: int = 0,
        character_length_cap: int = 8000,
        show_urls: bool = False,
    ) -> str:
        """Read the content of a web page and return it as Markdown text.

        Args:
            url (str): The URL of the web page to read.
            start_character (int): The starting character index from which to return the page content.
                Defaults to 0.
            character_length_cap (int): Maximum number of characters to return from the page content.
                Defaults to 8000 characters to protect the model's context window.
            show_urls (bool): Whether to show URLs in the extracted content. Defaults to False.

        Returns:
            str: The content of the web page as Markdown text.
        """
        # Set the mapping of HTML tags to Markdown formatting
        tag_mapping = {
            "h1": "# {text}\n",
            "h2": "## {text}\n",
            "h3": "### {text}\n",
            "h4": "#### {text}\n",
            "h5": "#### {text}\n",
            "h6": "#### {text}\n",
            "li": "- {text}",
            "blockquote": "> {text}\n",
            "pre": "```\n{text}\n```\n",
            "p": "{text}\n",
        }

        try:
            # Set a user-agent header to avoid being blocked by some websites
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }

            # Retrieve the HTML content of the page
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            tree = HTMLParser(response.text)

            # Remove non-content, boilerplate, sidebar, and metadata elements from the tree
            for tag in tree.css(
                (
                    "script, style, nav, footer, header, noscript, svg, form, iframe, aside, "
                    ".sidebar, .navbox, .infobox, .metadata, .mw-editsection, .mw-jump-link, "
                    "[role='navigation'], [role='complementary']"
                )
            ):
                tag.decompose()

            # Prefer main article body if available (e.g., Wikipedia #mw-content-text, article, main)
            root = (
                tree.css_first("main, article, #mw-content-text, #content")
                or tree.body
                or tree.root
            )

            # Convert <a> tags to Markdown [text](href) within content blocks
            for node in root.css(",".join(tag_mapping.keys())):
                self._convert_links_to_markdown(node, base_url=url, show_urls=show_urls)

            # Extract text from the relevant HTML tags and format them as Markdown
            markdown_parts: list[str] = []
            for node in root.css(",".join(tag_mapping.keys())):
                # Clean up any multiple spaces inside the block
                text = re.sub(r"[ \t]+", " ", node.text())

                # Fix spacing before punctuation attached to links: " )" -> ")" or " ," -> ","
                text = re.sub(r"\s+([,.;:!?\)])", r"\1", text)
                text = re.sub(r"(\()\s+", r"\1", text)

                # Remove citation references like [1], [2], [note 1] while preserving markdown
                # links [text](url)
                text = re.sub(
                    r"\[(?:\d+|[a-z]|note \d+|citation needed)\](?!\()",
                    "",
                    text,
                    flags=re.IGNORECASE,
                )

                if not text:
                    continue

                markdown_parts.append(
                    tag_mapping.get(node.tag or "", "{text}\n").format(text=text)
                )

            clean_markdown = "\n".join(markdown_parts)

            # If the cleaned markdown is empty, return a fallback message so the
            # model can handle it gracefully instead of returning an empty string.
            if not clean_markdown:
                return "<No readable content found at URL.>"

            clean_markdown = clean_markdown[start_character:].strip()

            # Cap character length to protect model context window
            if len(clean_markdown) > character_length_cap:
                return (
                    clean_markdown[:character_length_cap] + "\n\n[Content truncated...]"
                )

            return clean_markdown

        except Exception as e:
            logger.warning(
                "url_reader_failed tool=%s error_type=%s",
                self.name,
                type(e).__name__,
                exc_info=True,
            )
            return f"Error reading URL: {str(e)}"

    def to_groq_spec(self) -> dict[str, Any]:
        """Return the Groq/OpenAI tool specification."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
