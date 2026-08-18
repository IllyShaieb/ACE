"""Ensure the tools can be used as expected."""

from datetime import datetime
from unittest.mock import patch

import pytest

from src.tools import ClockTool, DuckDuckGoSearchTool, Tool, WolframAlphaTool


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
                        "error": {"msg": "Mocked error message"},
                    }
                },
                "Wolfram Alpha was unable to calculate a result for this query.",
                "Unsuccessful query with an error message",
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
