"""Ensure the tools can be used as expected."""

import logging
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.tools import (
    ClockTool,
    DuckDuckGoSearchTool,
    Tool,
    UrlReaderTool,
    WolframAlphaTool,
)


class TestClockTool:
    """Test suite for the ClockTool class."""

    def test_clock_tool_satisfies_tool_protocol(self):
        """Verify ClockTool conforms to the Tool interface."""
        # ARRANGE: Create an instance of ClockTool
        tool = ClockTool()

        # ACT & ASSERT: Check if ClockTool is an instance of Tool
        assert isinstance(tool, Tool), "ClockTool should satisfy the Tool protocol."
        assert tool.name, "ClockTool name should be 'clock'."
        assert tool.description, "ClockTool should have a description."
        assert isinstance(
            tool.parameters, dict
        ), "ClockTool parameters should be a dictionary."

    def test_clock_tool_execute_returns_current_time(self):
        """Verify ClockTool's execute method returns a valid ISO formatted time string."""
        # ARRANGE: Create an instance of ClockTool and set a fixed time for testing
        tool = ClockTool()
        fixed_time = datetime(2026, 8, 14, 15, 30, 0)

        # ACT: Execute the tool to get the current time
        with patch("src.tools.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_time
            result = tool.execute()

        # ASSERT: Check if the result is a valid ISO formatted string
        assert (
            result == fixed_time.isoformat()
        ), "ClockTool execute should return the current time in ISO format."

    def test_clock_tool_to_groq_spec(self):
        """Verify ClockTool's to_groq_spec method returns the correct specification.

        Expected output:
        ```
                {
                    "type": "function",
                    "function": {
                        "name": "<tool_name>",
                        "description": "<tool_description>",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "<parameter_name>": {
                                "type": "<type_of_expression>",
                                "description": "<description_of_expression>"
                                }
                            },
                            "required": ["<parameter_name>"]
                            }
                    }
                }
                ```
        """
        # ARRANGE: Create an instance of ClockTool
        tool = ClockTool()

        # ACT: Get the Groq specification
        spec = tool.to_groq_spec()

        # ASSERT: Check if the specification matches the expected values
        assert spec["type"] == "function", "The type should be 'function'."
        assert (
            spec["function"]["name"] == tool.name
        ), "The function name should match the tool's name."
        assert (
            spec["function"]["description"] == tool.description
        ), "The function description should match the tool's description."
        assert (
            spec["function"]["parameters"] == tool.parameters
        ), "The function parameters should match the tool's parameters."
        assert spec["required"] == [], "The required field should be an empty list."


class TestWolframAlphaTool:
    """Test suite for the WolframAlphaTool class."""

    def test_wolfram_alpha_tool_satisfies_tool_protocol(self):
        """Verify WolframAlphaTool conforms to the Tool interface."""
        # ARRANGE: Create an instance of WolframAlphaTool
        tool = WolframAlphaTool()

        # ACT & ASSERT: Check if WolframAlphaTool is an instance of Tool
        assert isinstance(
            tool, Tool
        ), "WolframAlphaTool should satisfy the Tool protocol."
        assert tool.name, "WolframAlphaTool name should be defined."
        assert tool.description, "WolframAlphaTool should have a description."
        assert isinstance(
            tool.parameters, dict
        ), "WolframAlphaTool parameters should be a dictionary."

    @pytest.mark.parametrize(
        "response_json, expected_output, reason",
        [
            (
                {
                    "queryresult": {
                        "success": True,
                        "pods": [
                            {
                                "title": "Result",
                                "subpods": [
                                    {"plaintext": "Mocked Wolfram Alpha response"}
                                ],
                            }
                        ],
                    }
                },
                "Result: Mocked Wolfram Alpha response",
                "Successful query with title and subpods",
            ),
            (
                {
                    "queryresult": {
                        "success": True,
                        "pods": [
                            {
                                "subpods": [
                                    {"plaintext": "Mocked Wolfram Alpha response"}
                                ],
                            }
                        ],
                    }
                },
                "Mocked Wolfram Alpha response",
                "Successful query without title but with subpods",
            ),
            (
                {
                    "queryresult": {
                        "success": False,
                        "error": {"status": "1000", "message": "Invalid appid"},
                    }
                },
                "Wolfram Alpha returned an API error.",
                "Unsuccessful query with structured API error",
            ),
            (
                {
                    "queryresult": {
                        "success": False,
                        "error": False,
                        "didyoumeans": {"val": "mars moons count"},
                    }
                },
                "Wolfram Alpha could not understand the query. Did you mean 'mars moons count'?",
                "Unsuccessful query with didyoumeans suggestion",
            ),
            (
                {
                    "queryresult": {
                        "success": False,
                        "error": False,
                    }
                },
                "Wolfram Alpha could not understand the query.",
                "Unsuccessful query with no suggestions",
            ),
            (
                {
                    "queryresult": {
                        "success": True,
                        "pods": [],
                    }
                },
                "No text result returned.",
                "Successful query with no pods",
            ),
        ],
    )
    def test_wolfram_alpha_tool_execute_returns_expected_response(
        self, response_json, expected_output, reason
    ):
        """Verify WolframAlphaTool's execute method returns a valid response."""
        # ARRANGE: Create an instance of WolframAlphaTool and set a mock response
        tool = WolframAlphaTool()
        mock_response = response_json

        # ACT: Execute the tool with a sample query
        with patch("src.tools.requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            result = tool.execute(query="How many moons does Mars have?")

        # ASSERT: Check if the result matches the mocked response
        assert (
            result == expected_output
        ), f"WolframAlphaTool execute should return the expected mocked response: {reason}"

    def test_wolfram_alpha_tool_to_groq_spec(self):
        """Verify WolframAlphaTool's to_groq_spec method returns the correct specification.

        Expected output:
        ```
                {
                    "type": "function",
                    "function": {
                        "name": "<tool_name>",
                        "description": "<tool_description>",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "<parameter_name>": {
                                "type": "<type_of_expression>",
                                "description": "<description_of_expression>"
                                }
                            },
                            "required": ["<parameter_name>"]
                            }
                    }
                }
                ```
        """
        # ARRANGE: Create an instance of WolframAlphaTool
        tool = WolframAlphaTool()

        # ACT: Get the Groq specification
        spec = tool.to_groq_spec()

        # ASSERT: Check if the specification matches the expected values
        assert spec["type"] == "function", "The type should be 'function'."
        assert (
            spec["function"]["name"] == tool.name
        ), "The function name should match the tool's name."
        assert (
            spec["function"]["description"] == tool.description
        ), "The function description should match the tool's description."
        assert (
            spec["function"]["parameters"] == tool.parameters
        ), "The function parameters should match the tool's parameters."
        assert spec["required"] == [
            "query"
        ], "The required field should contain 'query'."

    def test_wolfram_alpha_logs_warning_on_unsuccessful_query(self, caplog):
        """Verify that WolframAlphaTool logs a warning when the query is unsuccessful."""
        # ARRANGE: Create an instance of WolframAlphaTool and a mock response
        tool = WolframAlphaTool()
        mock_response = {
            "queryresult": {
                "success": False,
                "error": {"status": "500", "message": "Internal server error"},
            }
        }

        # ACT: Execute the tool with an invalid query to trigger a warning
        with caplog.at_level(logging.WARNING, logger="src.tools"):
            with patch("src.tools.requests.get") as mock_get:
                mock_get.return_value.json.return_value = mock_response
                tool.execute(query="invalid_query_that_fails")

        # ASSERT: Check if a warning about the failed Wolfram Alpha query was logged
        assert (
            "wolfram_alpha_failed" in caplog.text
        ), "A warning for a failed Wolfram Alpha query should be logged."
        assert (
            "failure_reason=api_error" in caplog.text
        ), "The failure reason should be recorded as api_error."
        warning = next(
            record for record in caplog.records if record.levelno == logging.WARNING
        )
        assert "error_status=500" in warning.getMessage()
        assert "Internal server error" not in warning.getMessage()

    def test_wolfram_alpha_no_result_log_excludes_query(self, caplog):
        """Verify that failed query parsing logs only safe metadata."""
        tool = WolframAlphaTool()
        query = "private@example.com account balance"
        mock_response = {"queryresult": {"success": False, "error": False}}

        with caplog.at_level(logging.WARNING, logger="src.tools"):
            with patch("src.tools.requests.get") as mock_get:
                mock_get.return_value.json.return_value = mock_response
                tool.execute(query=query)

        warning = next(
            record for record in caplog.records if record.levelno == logging.WARNING
        )
        assert "wolfram_alpha_failed" in warning.getMessage()
        assert "failure_reason=cannot_parse" in warning.getMessage()
        assert query not in warning.getMessage()

    def test_wolfram_alpha_logs_warning_on_failed_url_query(self, caplog):
        """Verify that WolframAlphaTool logs a warning when the request to the API fails."""
        # ARRANGE: Create an instance of WolframAlphaTool
        tool = WolframAlphaTool()

        # ACT: Execute the tool with a query that triggers a request exception
        with caplog.at_level(logging.WARNING, logger="src.tools"):
            with patch("src.tools.requests.get") as mock_get:
                mock_get.side_effect = Exception("mock_request_failure")
                tool.execute(query="any_query")

        # ASSERT: Check if a warning about the failed Wolfram Alpha query was logged
        assert (
            "wolfram_alpha_failed" in caplog.text
        ), "A warning for a failed Wolfram Alpha query should be logged."


class TestWebSearchTool:
    """Test suite for the WebSearchTool class."""

    def test_web_search_tool_satisfies_tool_protocol(self):
        """Verify WebSearchTool conforms to the Tool interface."""
        # ARRANGE: Create an instance of WebSearchTool
        from src.tools import DuckDuckGoSearchTool

        tool = DuckDuckGoSearchTool()

        # ACT & ASSERT: Check if WebSearchTool is an instance of Tool
        assert isinstance(tool, Tool), "WebSearchTool should satisfy the Tool protocol."
        assert tool.name, "WebSearchTool name should be defined."
        assert tool.description, "WebSearchTool should have a description."
        assert isinstance(
            tool.parameters, dict
        ), "WebSearchTool parameters should be a dictionary."

    def test_web_search_tool_execute_returns_formatted_results(self):
        """Verify WebSearchTool's execute method returns formatted search results."""
        # ARRANGE: Create an instance of WebSearchTool and set a mock response
        tool = DuckDuckGoSearchTool()
        mock_results = [
            {
                "title": "Mocked Title 1",
                "href": "http://example.com/1",
                "body": "Mocked snippet 1",
            },
            {
                "title": "Mocked Title 2",
                "href": "http://example.com/2",
                "body": "Mocked snippet 2",
            },
        ]

        # ACT: Execute the tool with a sample query
        with patch("src.tools.DDGS") as mock_ddgs:
            mock_ddgs.return_value.__enter__.return_value.text.return_value = (
                mock_results
            )
            result = tool.execute(query="Sample query", max_results=2)

        # ASSERT: Check if the result contains the expected formatted output
        assert (
            "Title: Mocked Title 1" in result
        ), "The result should contain the first mocked title."
        assert (
            "URL: http://example.com/1" in result
        ), "The result should contain the first mocked URL."
        assert (
            "Snippet: Mocked snippet 1" in result
        ), "The result should contain the first mocked snippet."
        assert (
            "Title: Mocked Title 2" in result
        ), "The result should contain the second mocked title."
        assert (
            "URL: http://example.com/2" in result
        ), "The result should contain the second mocked URL."
        assert (
            "Snippet: Mocked snippet 2" in result
        ), "The result should contain the second mocked snippet."

    def test_web_search_tool_handles_empty_results(self):
        """Verify WebSearchTool handles empty search results gracefully."""
        # ARRANGE: Create an instance of WebSearchTool and set a mock response
        tool = DuckDuckGoSearchTool()
        mock_results = []

        # ACT: Execute the tool with a sample query
        with patch("src.tools.DDGS") as mock_ddgs:
            mock_ddgs.return_value.__enter__.return_value.text.return_value = (
                mock_results
            )
            result = tool.execute(query="Sample query", max_results=2)

        # ASSERT: Check if the result indicates no results were found
        assert (
            result == "No search results found."
        ), "The result should indicate no search results."

    def test_web_search_tool_to_groq_spec(self):
        """Verify WebSearchTool's to_groq_spec method returns the correct specification.

        Expected output:
        ```
                {
                    "type": "function",
                    "function": {
                        "name": "<tool_name>",
                        "description": "<tool_description>",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "<parameter_name>": {
                                "type": "<type_of_expression>",
                                "description": "<description_of_expression>"
                                }
                            },
                            "required": ["<parameter_name>"]
                            }
                    }
                }
                ```
        """
        # ARRANGE: Create an instance of WebSearchTool
        tool = DuckDuckGoSearchTool()

        # ACT: Get the Groq specification
        spec = tool.to_groq_spec()

        # ASSERT: Check if the specification matches the expected values
        assert spec["type"] == "function", "The type should be 'function'."
        assert (
            spec["function"]["name"] == tool.name
        ), "The function name should match the tool's name."
        assert (
            spec["function"]["description"] == tool.description
        ), "The function description should match the tool's description."
        assert (
            spec["function"]["parameters"] == tool.parameters
        ), "The function parameters should match the tool's parameters."
        assert spec["required"] == [
            "query"
        ], "The required field should contain 'query'."

    def test_web_search_tool_logs_warning_on_failure(self, caplog):
        """Verify DuckDuckGoSearchTool logs a warning when the search fails."""
        # ARRANGE: Create an instance of DuckDuckGoSearchTool
        tool = DuckDuckGoSearchTool()

        # ACT: Execute the tool with a query that triggers an exception
        with patch("src.tools.DDGS") as mock_ddgs:
            mock_ddgs.return_value.__enter__.return_value.text.side_effect = Exception(
                "Search failed"
            )
            result = tool.execute(query="test query")

        # ASSERT: Check if a warning was logged
        assert (
            "web_search_failed" in caplog.text
        ), "A warning for web search failure should be logged."


class TestUrlReaderTool:
    """Test suite for the UrlReaderTool class."""

    def test_url_reader_tool_satisfies_tool_protocol(self):
        """Verify UrlReaderTool conforms to the Tool interface."""
        # ARRANGE: Create an instance of UrlReaderTool
        tool = UrlReaderTool()

        # ACT & ASSERT: Check if UrlReaderTool is an instance of Tool
        assert isinstance(tool, Tool), "UrlReaderTool should satisfy the Tool protocol."
        assert tool.name, "UrlReaderTool name should be defined."
        assert tool.description, "UrlReaderTool should have a description."
        assert isinstance(
            tool.parameters, dict
        ), "UrlReaderTool parameters should be a dictionary."

    def test_url_reader_tool_extracts_structured_markdown(self):
        """Verify UrlReaderTool extracts content with markdown headings and lists."""
        # ARRANGE: Create an instance of UrlReaderTool
        html_content = """
            <html>
                <head>
                    <title>Page Title</title>
                    <style>body { color: red; }</style>
                </head>
                <body>
                    <nav><a href="/">Home</a></nav>
                    <h1>Breaking News Story</h1>
                    <p>An initial overview paragraph detailing the event.</p>
                    <h2>Key Developments</h2>
                    <ul>
                        <li>First major discovery</li>
                        <li>Second key point</li>
                    </ul>
                    <blockquote>Official government statement quote.</blockquote>
                    <script>console.log("analytics tracking");</script>
                    <footer>Copyright 2026</footer>
                </body>
            </html>
            """

        tool = UrlReaderTool()

        # ACT: Execute the tool with a sample URL
        with patch("src.tools.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_get.return_value = mock_response

            result = tool.execute(url="https://example.com/article")

        # ASSERT: Check if the result contains the expected output
        assert (
            "# Breaking News Story" in result
        ), "The result should contain the main heading."
        assert (
            "An initial overview paragraph detailing the event." in result
        ), "The result should contain the overview paragraph."
        assert (
            "## Key Developments" in result
        ), "The result should contain the subheading for key developments."
        assert (
            "- First major discovery" in result
        ), "The result should contain the first key point in the list."
        assert (
            "- Second key point" in result
        ), "The result should contain the second key point in the list."
        assert (
            "> Official government statement quote." in result
        ), "The result should contain the blockquote for the official statement."

        assert (
            "console.log" not in result
        ), "The result should not contain any script content."
        assert (
            "color: red" not in result
        ), "The result should not contain any style content."
        assert (
            "Copyright 2026" not in result
        ), "The result should not contain any footer content."
        assert (
            "Home" not in result
        ), "The result should not contain any navigation content."

    def test_url_reader_tool_truncates_long_content(self):
        """Verify UrlReaderTool caps text length while preserving structure."""
        # ARRANGE: Create an instance of UrlReaderTool with a long HTML content
        paragraphs = "".join(
            [f"<p>Paragraph {i} content text.</p>" for i in range(300)]
        )
        html_content = f"<html><body><h1>Long Document</h1>{paragraphs}</body></html>"

        tool = UrlReaderTool()

        # ACT: Execute the tool with a sample URL and a character length cap
        with patch("src.tools.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_get.return_value = mock_response

            result = tool.execute(
                url="https://example.com/long-document", character_length_cap=500
            )

        # ASSERT: Check if the result is truncated and contains the expected output
        assert (
            len(result) <= 524
        ), "The result should be truncated to the specified character length cap (+ 24 with '[Content truncated...]')."
        assert (
            "# Long Document" in result
        ), "The result should contain the main heading."
        assert (
            "[Content truncated...]" in result
        ), "The result should indicate that content was truncated."

    def test_url_reader_tool_handles_network_failure(self):
        """Verify UrlReaderTool handles network failures gracefully."""
        # ARRANGE: Create an instance of UrlReaderTool
        tool = UrlReaderTool()

        # ACT: Execute the tool with a sample URL and simulate a network failure
        with patch("src.tools.requests.get") as mock_get:
            mock_get.side_effect = Exception("Network failure")
            result = tool.execute(url="https://example.com/failure")

        # ASSERT: Check if the result indicates a network failure
        assert (
            "Error reading URL" in result
        ), "The result should indicate a network failure occurred."

    def test_url_reader_tool_strips_sidebars_and_infoboxes(self):
        """Verify UrlReaderTool removes sidebars and infoboxes from the content."""
        # ARRANGE: Create an instance of UrlReaderTool with HTML content containing sidebars and infoboxes
        html_content = """
            <html>
                <body>
                    <h1>Main Article Heading</h1>
                    <p>Main article content paragraph.</p>
                    <div class="sidebar">Sidebar content that should be removed.</div>
                    <table class="infobox">
                        <tr><td>Infobox content that should be removed.</td></tr>
                    </table>
                </body>
            </html>
            """

        tool = UrlReaderTool()

        # ACT: Execute the tool with a sample URL
        with patch("src.tools.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_get.return_value = mock_response

            result = tool.execute(url="https://example.com/article-with-sidebar")

        # ASSERT: Check if the result does not contain sidebar or infobox content
        assert (
            "Sidebar content" not in result
        ), "The result should not contain any sidebar content."
        assert (
            "Infobox content" not in result
        ), "The result should not contain any infobox content."
        assert (
            "# Main Article Heading" in result
        ), "The result should contain the main article heading."
        assert (
            "Main article content paragraph." in result
        ), "The result should contain the main article paragraph."

        assert (
            "Sidebar content that should be removed." not in result
        ), "The result should not contain the sidebar content."
        assert (
            "Infobox content that should be removed." not in result
        ), "The result should not contain the infobox content."

    def test_url_reader_tool_formats_links_as_markdown(self):
        """Verify UrlReaderTool formats links as Markdown."""
        # ARRANGE: Create an instance of UrlReaderTool with HTML content containing links
        html_content = """
            <html>
                <body>
                    <p>Visit the <a href="https://gov.uk">Official Government Portal</a> for details.</p>
                    <ul>
                        <li>Read the <a href="https://example.com/manifesto">Manifesto</a> here.</li>
                    </ul>
                </body>
            </html>
            """

        tool = UrlReaderTool()

        # ACT: Execute the tool with a sample URL
        with patch("src.tools.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_get.return_value = mock_response

            result = tool.execute(
                url="https://example.com/article-with-links", show_urls=True
            )

        # ASSERT: Check if the result contains the link formatted as Markdown
        assert (
            "[Official Government Portal](https://gov.uk)" in result
        ), "The result should contain the link formatted as Markdown."
        assert (
            "- Read the [Manifesto](https://example.com/manifesto) here." in result
        ), "The result should contain the list item with the link formatted as Markdown."

    def test_url_reader_tool_preserves_spaces_around_links(self):
        """Verify UrlReaderTool ensures whitespace separation around markdown links."""
        # ARRANGE: Create an instance of UrlReaderTool with HTML content containing links
        html_content = """
        <html>
            <body>
                <p>capability of <a href="https://example.com/computer">computational systems</a> to perform tasks</p>
            </body>
        </html>
        """

        tool = UrlReaderTool()

        # ACT: Execute the tool with a sample URL
        with patch("src.tools.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_get.return_value = mock_response

            result = tool.execute(
                url="https://example.com/article-with-links", show_urls=True
            )

        # ASSERT: Check if the result contains the link formatted as Markdown with proper spacing
        assert (
            "capability of [computational systems](https://example.com/computer) to perform tasks"
            in result
        ), "The result should contain the link formatted as Markdown with proper spacing."

    def test_url_reader_tool_handles_empty_content(self):
        """Verify UrlReaderTool handles pages with no readable content gracefully."""
        # ARRANGE: Create an instance of UrlReaderTool with HTML content that has no readable content
        html_content = """
            <html>
                <body>
                    <div class="sidebar">Sidebar content only.</div>
                    <div class="infobox">Infobox content only.</div>
                </body>
            </html>
            """

        tool = UrlReaderTool()

        # ACT: Execute the tool with a sample URL
        with patch("src.tools.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_get.return_value = mock_response

            result = tool.execute(url="https://example.com/empty-content")

        # ASSERT: Check if the result indicates no readable content was found
        assert (
            "<No readable content found at URL.>" in result
        ), "The result should indicate that no readable content was found."

    def test_url_reader_tool_to_groq_spec(self):
        """Verify UrlReaderTool's to_groq_spec method returns the correct specification.

        Expected output:
        ```
                {
                    "type": "function",
                    "function": {
                        "name": "<tool_name>",
                        "description": "<tool_description>",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "<parameter_name>": {
                                "type": "<type_of_expression>",
                                "description": "<description_of_expression>"
                                }
                            },
                            "required": ["<parameter_name>"]
                            }
                    }
                }
                ```
        """
        # ARRANGE: Create an instance of UrlReaderTool
        tool = UrlReaderTool()

        # ACT: Get the Groq specification
        spec = tool.to_groq_spec()

        # ASSERT: Check if the specification matches the expected values
        assert spec["type"] == "function", "The type should be 'function'."
        assert (
            spec["function"]["name"] == tool.name
        ), "The function name should match the tool's name."
        assert (
            spec["function"]["description"] == tool.description
        ), "The function description should match the tool's description."
        assert (
            spec["function"]["parameters"] == tool.parameters
        ), "The function parameters should match the tool's parameters."
        assert spec["function"]["parameters"]["required"] == [
            "url"
        ], "The required field should contain 'url'."

    def test_url_reader_tool_logs_warning_on_failure(self, caplog):
        """Verify UrlReaderTool logs a warning when reading a URL fails."""
        # ARRANGE: Create an instance of UrlReaderTool
        tool = UrlReaderTool()

        # ACT: Execute the tool with a query that triggers an exception
        with patch("src.tools.requests.get") as mock_get:
            mock_get.side_effect = Exception("Request failed")
            result = tool.execute(url="http://example.com")

        # ASSERT: Check if a warning was logged
        assert (
            "url_reader_failed" in caplog.text
        ), "A warning for URL reader failure should be logged."
