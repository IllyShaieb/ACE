"""main.py: Entry point for the ACE application.

Handles the wiring of concrete components via Dependency Injection.
"""

import asyncio
import os

from dotenv import load_dotenv
from google import genai

from core.adapters import RequestsHTTPAdapter, RichIOAdapter
from core.models import GeminiIntelligenceModel
from core.presenters import ConsolePresenter
from core.services import IPInfoLocationService, OpenWeatherMapService
from core.views import ConsoleView

load_dotenv()

# Configuration
CONFIG = {
    "WELCOME_MESSAGE": """
###############################################################
#           ACE - The Artificial Consciousness Engine         #
###############################################################

Type your queries below. To exit, type 'exit' or press Ctrl+C.

""",
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "OPENWEATHERMAP_API_KEY": os.getenv("OPENWEATHERMAP_API_KEY"),
}


def verify_config():
    """Verify that all required configuration values are present."""
    missing_keys = [key for key, value in CONFIG.items() if not value]
    if missing_keys:
        raise ValueError(
            f"Missing required configuration values: {', '.join(missing_keys)}. "
            "Please set them in the .env file or environment variables."
        )


async def main_async():
    """Initialize the model, view, and presenter, then run the application."""
    # 1. Verify configuration before starting the application
    verify_config()

    # 2. Create the low-level I/O hardware
    io_adapter = RichIOAdapter()
    http_adapter = RequestsHTTPAdapter()

    # 3. Initialize the Passive View with the adapter
    view = ConsoleView(io_adapter=io_adapter)

    # 4. Initialize the Gemini Intelligence Model (The Brain)
    services_registry = {
        "weather_service": OpenWeatherMapService(
            http_client_adapter=http_adapter, api_key=CONFIG["OPENWEATHERMAP_API_KEY"]
        ),
        "location_service": IPInfoLocationService(http_client_adapter=http_adapter),
    }

    # Specify a list of available models for the Gemini Intelligence Model, starting with the most
    # capable model and including fallback options. This allows the model to gracefully degrade to
    # less capable models if the most capable one is unavailable or encounters issues.
    available_models = [
        "gemini-3.1-flash-lite-preview",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]
    model = GeminiIntelligenceModel(
        client=genai.Client(api_key=CONFIG["GEMINI_API_KEY"]),
        services=services_registry,
        model=available_models[0],  # Start with the most capable model
        fallback_models=available_models[1:],  # All except the most capable model,
    )

    # 5. Inject View and Model into the Presenter (The Switchboard)
    presenter = ConsolePresenter(
        model=model, view=view, welcome_message=CONFIG["WELCOME_MESSAGE"]
    )

    # 6. Execute
    try:
        await presenter.run()
    except KeyboardInterrupt:
        print("\nACE safely interrupted. Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        pass
    finally:
        print("\nACE safely interrupted. Goodbye!")
