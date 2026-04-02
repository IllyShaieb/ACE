"""tests.services.test_location: Ensure the location service can fetch location information."""

import unittest
from unittest.mock import MagicMock

from core import services
from core.protocols import HTTPClientAdapterProtocol


class TestIPInfoLocationService(unittest.TestCase):
    """Test the IPInfoLocationService's ability to fetch location information based on the client's IP address."""

    def setUp(self):
        """Set up common test components."""
        self.mock_http_client_adapter = MagicMock(spec=HTTPClientAdapterProtocol)
        self.location_service = services.IPInfoLocationService(
            self.mock_http_client_adapter, api_key="test_api_key"
        )

    def test_get_location_success(self):
        """Verify that `get_location()` returns a dictionary with location information."""
        # ARRANGE: Define the expected location information and mock the HTTP client's response
        expected_location_info = {
            "city": "London",
            "region": "England",
            "country": "GB",
            "loc": "51.5073,-0.1276",
        }
        self.mock_http_client_adapter.get.return_value = expected_location_info

        # ACT: Call the `get_location()` method
        result = self.location_service.get_location()

        # ASSERT: Verify that the result matches the expected location information
        self.assertEqual(result, expected_location_info)

    def test_get_location_failure(self):
        """Verify the service handles API failures gracefully."""
        # ARRANGE: Mock the API to raise a RuntimeError
        self.mock_http_client_adapter.get.side_effect = RuntimeError("API failure")

        # ACT & ASSERT: Call the `get_location()` method and expect a RuntimeError
        with self.assertRaises(RuntimeError):
            self.location_service.get_location()


if __name__ == "__main__":
    unittest.main()
