"""tests.models.test_gemini: Test the GeminiModel class to ensure it processes queries correctly
and returns expected responses."""

import unittest
from typing import Optional
from unittest.mock import MagicMock, Mock

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from core.adapters.protocols import ConversationStorageAdapterProtocol
from core.models import GeminiIntelligenceModel
from core.tools.protocols import ToolProtocol


class TestGeminiIntelligenceModel(unittest.IsolatedAsyncioTestCase):
    """Test the GeminiIntelligenceModel's ability to process queries and return responses."""

    async def asyncSetUp(self):
        """Set up common test components."""
        self.mock_client = Mock(spec=genai.Client)
        self.mock_storage = MagicMock(spec=ConversationStorageAdapterProtocol)

        # Configure the cache mock: Mock.name is a special attribute so we must set
        # it explicitly via configure_mock to ensure it returns a predictable string.
        mock_cache = MagicMock()
        mock_cache.configure_mock(name="cachedContents/test-cache-id")
        self.mock_client.caches.create.return_value = mock_cache

        self.model = GeminiIntelligenceModel(
            self.mock_client, tools=[], storage_adapter=self.mock_storage
        )

    def _create_mock_response(
        self, text: Optional[str] = None, function_call: Optional[MagicMock] = None
    ) -> MagicMock:
        """Helper to create a nested Gemini response structure.

        ```
        Part -> Content -> Candidate -> GenerateContentResponse
        ```

        Args:
            text (Optional[str]): The text to include in the response part.
            function_call (Optional[MagicMock]): A mock representing a function call, if any.

        Returns:
            MagicMock: A mock representing the nested Gemini response structure.
        """
        # 1. Part: Represents a segment of the response, which can be text or a function call
        part = MagicMock(
            spec=types.Part, text=text, function_call=function_call, thought=False
        )

        # 2. Content: Contains one or more parts
        content = MagicMock(spec=types.Content, parts=[part])

        # 3. Candidate: Represents a single candidate response, which includes content
        candidate = MagicMock(spec=types.Candidate, content=content)

        # 4. GenerateContentResponse: The top-level response object containing candidates
        return MagicMock(spec=types.GenerateContentResponse, candidates=[candidate])

    async def test_prepare_tools(self):
        """Verify that `_prepare_tools()` correctly prepares the tools for use with the Gemini API."""
        # ARRANGE: Define a set of mock tools and the expected prepared tools
        mock_tool_1 = MagicMock(spec=ToolProtocol)
        mock_tool_1.name = "tool_one"
        mock_tool_1.description = "First test tool."
        mock_tool_1.parameters_schema = {
            "type": "OBJECT",
            "properties": {},
            "required": [],
        }

        mock_tool_2 = MagicMock(spec=ToolProtocol)
        mock_tool_2.name = "tool_two"
        mock_tool_2.description = "Second test tool."
        mock_tool_2.parameters_schema = {
            "type": "OBJECT",
            "properties": {
                "input": {"type": "STRING"},
            },
            "required": ["input"],
        }

        self.model.tools = [mock_tool_1, mock_tool_2]

        # ACT: Prepare the tools using the model's method
        prepared_tools = self.model._format_tools_for_gemini()

        # ASSERT: Verify that the prepared tools match the expected format for the Gemini API
        self.assertIsInstance(prepared_tools, list)
        for tool in prepared_tools:
            self.assertIsInstance(tool, types.FunctionDeclaration)
        self.assertEqual(len(prepared_tools), 2)

    async def test_context_cache_is_created_on_init(self):
        """Verify that a context cache is created during initialisation with the correct config."""
        # ASSERT: The cache was created once during setUp
        self.mock_client.caches.create.assert_called_once()

        call_kwargs = self.mock_client.caches.create.call_args
        self.assertIn("models/", call_kwargs.kwargs["model"])

        cache_config = call_kwargs.kwargs["config"]
        self.assertIsNotNone(cache_config.system_instruction)
        self.assertIsNotNone(cache_config.tools)
        self.assertEqual(cache_config.ttl, "3600s")

    async def test_chat_session_references_cache(self):
        """Verify that the chat session is configured to use the context cache."""
        # ACT: Load a session to trigger chat creation
        self.model.load_session()

        # ASSERT: The chat was created with a cached_content reference
        self.mock_client.chats.create.assert_called_once()

        call_kwargs = self.mock_client.chats.create.call_args
        chat_config = call_kwargs.kwargs["config"]
        self.assertEqual(chat_config.cached_content, "cachedContents/test-cache-id")

    async def test_close_deletes_cache(self):
        """Verify that close() deletes the context cache and clears the reference."""
        # ACT: Close the model
        self.model.close()

        # ASSERT: The cache was deleted and the reference cleared
        self.mock_client.caches.delete.assert_called_once_with(
            name="cachedContents/test-cache-id"
        )
        self.assertIsNone(self.model._cache)

    async def test_close_is_idempotent(self):
        """Verify that calling close() twice does not raise an error."""
        # ACT: Close the model twice
        self.model.close()
        self.model.close()

        # ASSERT: The cache was deleted only once
        self.mock_client.caches.delete.assert_called_once()

    async def test_falls_back_to_direct_config_when_cache_too_small(self):
        """Verify that initialisation falls back to direct system_instruction/tools config
        when the context cache cannot be created because the content is too small."""
        # ARRANGE: Simulate the API rejecting the cache with a ClientError
        fallback_client = Mock(spec=genai.Client)
        fallback_client.caches.create.side_effect = genai_errors.ClientError(
            400,
            response_json={
                "error": {
                    "code": 400,
                    "message": "Cached content is too small.",
                    "status": "INVALID_ARGUMENT",
                }
            },
        )

        # ACT: Construct the model; this should not raise
        fallback_model = GeminiIntelligenceModel(
            fallback_client, tools=[], storage_adapter=self.mock_storage
        )
        fallback_model.load_session()

        # ASSERT: No cache is stored
        self.assertIsNone(fallback_model._cache)

        # ASSERT: The chat was still created, using system_instruction and tools directly
        fallback_client.chats.create.assert_called_once()
        call_kwargs = fallback_client.chats.create.call_args
        chat_config = call_kwargs.kwargs["config"]
        self.assertIsNotNone(chat_config.system_instruction)
        self.assertIsNotNone(chat_config.tools)

    async def test_process_query_direct_response(self):
        """Verify process_query returns text directly when no tools are requested."""
        # ARRANGE: Setup mocks for a simple response without tool calls
        expected_text = "Hello, how can I help?"
        mock_response = self._create_mock_response(text=expected_text)

        self.model.chat = MagicMock()
        self.model.chat.send_message.return_value = mock_response

        # ACT: Process a query using the model
        result = await self.model.process_query("Hi")

        # ASSERT: Verify the result is as expected and that the chat's
        # send_message method was called correctly
        self.assertEqual(result, expected_text)
        self.model.chat.send_message.assert_called_once_with("Hi")

    async def test_process_query_with_tool_execution(self):
        """Verify process_query handles the full Intent -> Execution -> Synthesis loop."""
        # ARRANGE
        # Mock tool setup: Create a mock tool that the model can call during processing
        mock_tool = MagicMock(spec=ToolProtocol)
        mock_tool.name = "get_weather"
        mock_tool.execute.return_value = "Sunny, 25°C"
        self.model.tools = [mock_tool]

        # Mock the response to the initial query to include a function call to the tool
        mock_function_call = MagicMock(args={"location": "London"})
        mock_function_call.name = "get_weather"
        final_text = "The weather in London is Sunny, 25°C."
        self.model.chat = MagicMock()
        self.model.chat.send_message.side_effect = [
            self._create_mock_response(function_call=mock_function_call),
            self._create_mock_response(text=final_text),
        ]

        # ACT: Process a query that triggers the tool execution flow
        result = await self.model.process_query("What is the weather in London?")

        # ASSERT: Verify the final result is correct and that the tool was executed
        # with the expected parameters
        self.assertEqual(result, final_text)
        mock_tool.execute.assert_called_once_with(location="London")
        self.assertEqual(self.model.chat.send_message.call_count, 2)

    async def test_process_query_tool_execution_failure(self):
        """Verify process_query catches local tool exceptions and feeds them back to the model."""
        # ARRANGE
        # Mock tool setup: Create a mock tool that raises an exception when executed
        mock_tool = MagicMock(spec=ToolProtocol)
        mock_tool.name = "failing_tool"
        mock_tool.execute.side_effect = Exception("Tool execution failed")
        self.model.tools = [mock_tool]

        # Mock the response to the initial query to include a function call to the failing tool
        mock_function_call = MagicMock(args={"input": "test"})
        mock_function_call.name = "failing_tool"
        self.model.chat = MagicMock()
        self.model.chat.send_message.side_effect = [
            self._create_mock_response(function_call=mock_function_call),
            self._create_mock_response(
                text="An error occurred while executing the tool."
            ),
        ]

        # ACT: Process a query that triggers the tool execution flow
        result = await self.model.process_query(
            "Run the failing tool with input 'test'."
        )

        # ASSERT: Verify that the model returns an error message and that the tool's execute method was called
        self.assertEqual(result, "An error occurred while executing the tool.")
        mock_tool.execute.assert_called_once_with(input="test")

    async def test_process_query_handles_server_error(self):
        """Verify process_query surfaces the API error and resets the chat session."""
        # ARRANGE: Mock the chat's send_message to raise a ServerError, and ensure
        # chats.create is available so the session-rebuild in the handler can run.
        self.model.chat = MagicMock()
        self.model.chat.send_message.side_effect = genai_errors.ServerError(
            500, response_json={}
        )
        self.mock_client.chats.create.reset_mock()

        # ACT: Process a query that triggers the API call
        result = await self.model.process_query("Trigger server error")

        # ASSERT: The error message is surfaced and the chat session is rebuilt.
        self.assertIn("error", result.lower())
        self.mock_client.chats.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
