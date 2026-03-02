"""core.adapters: This module defines adapters for the ACE application, providing
a layer of abstraction for different APIs the tools might depend on."""

from typing import Any, Dict, Optional

import requests

##################################################################################
#                                  VIEW ADAPTERS                                 #
##################################################################################


class BuiltinIOAdapter:
    """
    The 'Standard' implementation of I/O.

    Simply wraps Python's built-in functions to satisfy the IOAdapter contract.
    """

    def get_input(self, prompt: str) -> str:
        return input(prompt)

    def display_output(self, message: str) -> None:
        print(message)

    def start_loading_indicator(self, message: str) -> None:
        return

    def stop_loading_indicator(self) -> None:
        return


#################################################################################
#                                  SERVICES ADAPTERS                            #
#################################################################################


class RequestsHTTPAdapter:
    """Adapter for making HTTP requests using the 'requests' library."""

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a GET request to the specified URL with optional query parameters.

        Args:
            url (str): The URL to send the GET request to.
            params (Optional[Dict[str, Any]]): Optional query parameters for the GET request.
            headers (Optional[Dict[str, Any]]): Optional headers for the GET request.

        Returns:
            Any: The JSON response from the GET request. May be a dictionary, list etc.
                depending on the API response.

        Raises:
            RuntimeError: If the HTTP request fails or returns an error status code.
        """
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP GET failed: {e}")

    def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a POST request to the specified URL with form data or JSON payload.

        Args:
            url (str): The URL to send the POST request to.
            data (Optional[Any]): Form-encoded data, bytes, or file objects.
            json (Optional[Dict]): JSON-serializable dictionary payload.
            headers (Optional[Dict[str, Any]]): Optional HTTP headers.

        Returns:
            Any: The JSON response from the POST request. May be a dictionary, list etc.
                depending on the API response.

        Raises:
            RuntimeError: If the HTTP request fails or returns an error status code.
        """
        try:
            response = requests.post(url, data=data, json=json, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP POST failed: {e}")
