import os
import warnings

import weatherapi
from cachetools import TTLCache, cached


@cached(cache=TTLCache(maxsize=60, ttl=300))
def get_weather(location: str) -> dict:
    """Get the weather for a location."""
    # Suppress warnings from the weatherapi library
    warnings.filterwarnings("ignore", module="weatherapi")

    # Setup the WeatherAPI configuration
    weatherapi_config = weatherapi.Configuration()
    weatherapi_config.api_key["key"] = os.environ.get("ACE_WEATHER_API_KEY")

    weatherapi_instance = weatherapi.APIsApi(weatherapi.ApiClient(weatherapi_config))

    return weatherapi_instance.realtime_weather(q=location)
