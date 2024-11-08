import os
from datetime import date, timedelta

import weatherapi
from cachetools import TTLCache, cached


@cached(cache=TTLCache(maxsize=60, ttl=300))
def get_weather(location: str, future_days: int = 0) -> dict:
    """Get the weather for a location."""
    # Setup the WeatherAPI configuration
    weatherapi_config = weatherapi.Configuration()
    weatherapi_config.api_key["key"] = os.environ.get("ACE_WEATHER_API_KEY")

    weatherapi_instance = weatherapi.APIsApi(weatherapi.ApiClient(weatherapi_config))

    if future_days >= 1:
        forecast_date = date.today() + timedelta(days=future_days)
        return weatherapi_instance.forecast_weather(
            q=location, dt=forecast_date.strftime("%Y-%m-%d"), days=future_days
        )
    else:
        return weatherapi_instance.realtime_weather(q=location)
