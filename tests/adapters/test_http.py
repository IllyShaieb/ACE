"""tests.adapters.test_http: Ensures that the HTTP adapter in the ACE application is functioning correctly."""

import unittest
from unittest.mock import MagicMock, patch

import requests

from core import adapters


class TestRequestsHTTPAdapter(unittest.TestCase):
    """Test the RequestsHTTPAdapter's ability to make GET and POST requests using the
    'requests' library."""

    def setUp(self) -> None:
        """Set up common test components."""
        self.adapter = adapters.RequestsHTTPAdapter()
        self.test_url = "https://api.example.com/test"

    @patch("core.adapters.http.requests.get")
    def test_get_success(self, mock_get):
        """Test that the GET method makes a GET request using the 'requests' library."""
        # ARRANGE: Set up the mock response for the GET request
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        test_parameters = {"param1": "value1"}
        test_headers = {"Authorization": "Bearer testtoken"}

        # ACT: Call the GET method of the adapter
        result = self.adapter.get(
            self.test_url, params=test_parameters, headers=test_headers
        )

        # ASSERT: Verify that the GET request was made with the correct parameters
        mock_get.assert_called_once_with(
            self.test_url, params=test_parameters, headers=test_headers
        )
        self.assertEqual(result, {"key": "value"})

    @patch("core.adapters.http.requests.get")
    def test_get_failure(self, mock_get):
        """Test that the GET method raises an exception for HTTP errors."""
        # ARRANGE: Set up the mock to raise an HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.RequestException(
            "HTTP error"
        )
        mock_get.return_value = mock_response

        # ACT & ASSERT: Verify it gets translated to a RuntimeError
        with self.assertRaises(RuntimeError) as context:
            self.adapter.get(self.test_url)

        self.assertIn("HTTP GET failed", str(context.exception))

    @patch("core.adapters.http.requests.post")
    def test_post_success(self, mock_post):
        """Test that the POST method makes a POST request using the 'requests' library."""
        # ARRANGE: Set up the mock response and test data for the POST request
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_post.return_value = mock_response

        test_cases = [
            {
                "data": None,
                "json": {"key": "value"},
                "headers": None,
                "description": "POST request with JSON payload",
            },
            {
                "data": {"field": "value"},
                "json": None,
                "headers": {"Content-Type": "application/x-www-form-urlencoded"},
                "description": "POST request with form data",
            },
            {
                "data": None,
                "json": None,
                "headers": None,
                "description": "POST request with no data",
            },
            {
                "data": {"field": "value"},
                "json": {"key": "value"},
                "headers": {"Content-Type": "application/json"},
                "description": "POST request with both form data and JSON payload",
            },
        ]

        for case in test_cases:
            with self.subTest(case["description"]):
                # ACT: Call the POST method of the adapter
                result = self.adapter.post(
                    self.test_url,
                    data=case["data"],
                    json=case["json"],
                    headers=case["headers"],
                )

                # ASSERT: Verify that the POST request was made with the correct
                # parameters
                mock_post.assert_called_with(
                    self.test_url,
                    data=case["data"],
                    json=case["json"],
                    headers=case["headers"],
                )
                self.assertEqual(result, {"key": "value"})

    @patch("core.adapters.http.requests.post")
    def test_post_failure(self, mock_post):
        """Test that the POST method raises an exception for HTTP errors."""
        # ARRANGE: Set up the mock to raise an HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.RequestException(
            "HTTP error"
        )
        mock_post.return_value = mock_response

        # ACT & ASSERT: Verify that an exception is raised when calling the POST method
        with self.assertRaises(RuntimeError) as context:
            self.adapter.post(self.test_url)

        self.assertIn("HTTP POST failed", str(context.exception))


if __name__ == "__main__":
    unittest.main()
