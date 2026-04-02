"""core.services.location: Services for fetching location information."""

from typing import Dict, Optional

from core.adapters.protocols import HTTPClientAdapterProtocol, LogStorageAdapterProtocol


class IPInfoLocationService:
    """Service for fetching location information based on IP address using the ipinfo.io API."""

    def __init__(
        self,
        http_client_adapter: HTTPClientAdapterProtocol,
        api_key: Optional[str] = None,
        log_storage_adapter: Optional[LogStorageAdapterProtocol] = None,
    ):
        """Initialize the IPInfoLocationService with an HTTP client adapter and API key.

        Args:
            http_client_adapter (HTTPClientAdapterProtocol): An adapter for making HTTP requests.
            api_key (Optional[str]): The API key for accessing the ipinfo.io API.
            log_storage_adapter (Optional[LogStorageAdapterProtocol]): An optional adapter for
                logging events related to the location service. Defaults to None.
        """
        self.http_client_adapter = http_client_adapter
        self.api_key = api_key
        self.log_storage_adapter = log_storage_adapter

        url_config = {
            "base": "https://ipinfo.io",
            "endpoints": {
                "free": "/json",
                "lite": "/lite/me?token={api_key}",
            },
        }
        self.url = (
            url_config["base"] + url_config["endpoints"]["lite"].format(api_key=api_key)
            if api_key
            else url_config["base"] + url_config["endpoints"]["free"]
        )

    def _log_event(
        self, level: str, source: str, message: str, details: Optional[str] = None
    ) -> None:
        """Log an event to the log storage adapter.

        Args:
            level (str): The severity level of the event (e.g., "INFO", "ERROR").
            source (str): The source of the event (e.g., "model", "tool").
            message (str): A descriptive message about the event.
            details (Optional[str]): Additional details or context about the event.
        """
        if self.log_storage_adapter:
            self.log_storage_adapter.log_event(
                level=level, source=source, message=message, details=details
            )

    def get_location(self) -> Dict[str, str]:
        """Get the location information based on the client's IP address.

        Returns:
            Dict[str, str]: The location information including city, region, country, and coordinates.
        """
        self._log_event(
            level="INFO",
            source="location_service",
            message="Fetching location information based on IP address",
        )

        try:
            if self.api_key:
                response = self.http_client_adapter.get(
                    self.url, headers={"Authorization": f"Bearer {self.api_key}"}
                )
            else:
                response = self.http_client_adapter.get(self.url)
            return {
                "city": response.get("city"),
                "region": response.get("region"),
                "country": response.get("country"),
                "loc": response.get("loc"),  # Latitude and Longitude
            }
        except RuntimeError as e:
            self._log_event(
                level="ERROR",
                source="location_service",
                message="Failed to fetch location information based on IP address",
                details=str(e),
            )
            raise RuntimeError(f"Failed to fetch location data: {e}")
