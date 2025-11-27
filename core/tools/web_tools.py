"""core.tools.web: Tools for external and web retrieval functionalities."""

import os
import random
import time
from concurrent import futures

import cachetools
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from core.constants import WEATHER_API_TIMEOUT, WEATHER_API_URL, WEB_CLIENT_USER_AGENTS
from core.tools import TOOL_HANDLERS, register_tool


@register_tool(
    name="GET_WEATHER",
    description="Fetches and returns the current weather for a specified location.",
    registry=TOOL_HANDLERS,
)
def get_weather(location: str) -> str:
    """
    Fetches weather data from an external API and formats it into a human-readable response.

    Args:
        location (str): The location to fetch the weather for.

    Returns:
        str: A human-readable string with the current weather information.
    """
    if not location:
        return "What location would you like to know the weather for?"

    if not (api_key := os.getenv("WEATHER_API_KEY")):
        return "Apologies, it appears the WEATHER_API_KEY is not set."

    try:
        api_response = requests.get(
            WEATHER_API_URL,
            params={"key": api_key, "q": location},
            timeout=WEATHER_API_TIMEOUT,
        )
        api_response.raise_for_status()
        data = api_response.json()

    except requests.RequestException as e:
        return f"An error occurred while fetching the weather data: {e.__class__.__name__} - {e}"

    try:
        # Extract relevant weather details
        location_name = data["location"]["name"]
        region = data["location"]["region"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        wind_kph = data["current"]["wind_kph"]
        humidity = data["current"]["humidity"]
        feelslike_c = data["current"]["feelslike_c"]

        # Format the response
        return (
            f"Weather in {location_name}, {region}, {country}:\n"
            f"Temperature: {temp_c}°C\n"
            f"Condition: {condition}\n"
            f"Wind Speed: {wind_kph} kph\n"
            f"Humidity: {humidity}%\n"
            f"Feels Like: {feelslike_c}°C"
        )

    except KeyError as e:
        return f"Received unexpected data format from the weather service: {e.__class__.__name__} - {e}"


@cachetools.cached(cachetools.LRUCache(maxsize=1))
def get_summarizer():
    """Returns a singleton instance of the WebPageSummarizer.

    Cached to ensure we don't re-initialise the LLM client unnecessarily.
    """
    # Import here to avoid circular dependency at module level
    from core.llm import WebPageSummarizer

    return WebPageSummarizer()


# Use a 10 minute time-to-use cache to balance freshness and performance
@cachetools.cached(cachetools.TTLCache(maxsize=1024, ttl=600))
def scrape_and_summarise(url: str, query: str) -> str:
    """Scrapes the content of a URL and summarizes it.

    Args:
        url (str): The URL to scrape.
        query (str): The original search query.

    Returns:
        str: A formatted summary of the scraped content.
    """
    # Retrieve the singleton summarizer
    summarizer = get_summarizer()

    # Use requests to call the url
    response = requests.get(
        url,
        timeout=30,
        headers={
            # Use a random User-Agent to help avoid blocks
            "User-Agent": random.choice(WEB_CLIENT_USER_AGENTS)
        },
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script, style, and navigation elements to clean up the text
    for element in soup.find_all(
        ["script", "style", "nav", "footer", "header", "aside", "noscript"]
    ):
        element.decompose()

    # Try to find the main content area, falling back to body
    content_element = soup.find("main") or soup.find("article") or soup.find("body")

    if content_element:
        text_content = content_element.get_text(separator="\n", strip=True)
    else:
        # Fallback if no specific container is found
        text_content = soup.get_text(separator="\n", strip=True)

    summary = summarizer(text_content, query)

    # Add delay to respect rate limits
    time.sleep(2)

    return summary


@register_tool(
    name="WEB_SEARCH",
    description="Performs a web search and returns a summary of results.",
    registry=TOOL_HANDLERS,
)
def web_search(query: str) -> str:
    """
    Performs a web search, scrapes the top results, and provides a summary.

    Args:
        query (str): The search query provided by the user.

    Returns:
        str: A summary of the top search results.
    """
    if not query:
        return "What would you like to search for?"

    # Setup headers for the summary
    main_header = f'# Search Results for: "{query}"\n'

    # Perform web and news searches and gather the results
    # so that we can format them later
    base_dict = {
        "header": None,
        "results": [],
        "title_ref": "title",
        "url_ref": None,
        "body_ref": "body",
        "date_ref": None,
        "source_ref": None,
    }
    with DDGS() as ddgs:
        web_search_results = []

        # Text results
        web_search_results.append(
            {
                **base_dict,
                "header": "## Text Results",
                "results": list(
                    ddgs.text(
                        query,
                        region="wt-en",
                        max_results=5,
                    )
                ),
                "url_ref": "href",
            }
        )

        # News results
        web_search_results.append(
            {
                **base_dict,
                "header": "## News Results",
                "results": list(
                    ddgs.news(
                        query,
                        region="wt-en",
                        max_results=5,
                    )
                ),
                "url_ref": "url",
                "date_ref": "date",
                "source_ref": "source",
            }
        )

    # Get all URLs to be scraped
    urls_to_scrape = [
        result.get(results["url_ref"])
        for results in web_search_results
        for result in results["results"]
    ]

    # Scrape and summarise the URLs using a thread pool for concurrency
    # to improve performance
    scraped_data = {}
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Map URLs to their future summaries so we can track them
        future_to_url = {
            executor.submit(scrape_and_summarise, url, query): url
            for url in urls_to_scrape
        }

        # As each future completes, store the result
        for future in futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                summary = future.result()
                scraped_data[url] = summary
            except Exception as e:
                scraped_data[url] = (
                    f"Error retrieving summary: {e.__class__.__name__} - {e}"
                )

    # Now format the final output
    final_output = main_header + "\n"
    for results in web_search_results:
        if not results["results"]:
            continue

        final_output += f"\n{results['header']}\n\n"

        for result in results["results"]:
            title = result.get(results["title_ref"], "No Title")
            url = result.get(results["url_ref"], "No URL")
            body = result.get(results["body_ref"], "")
            date = result.get(results["date_ref"], "")
            source = result.get(results["source_ref"], "")

            final_output += f"### [{title}]({url})\n"
            if date:
                final_output += f"*Published on: {date}*\n\n"
            if source:
                final_output += f"*Source: {source}*\n\n"
            if body:
                final_output += f"**Body:** {body}\n\n"
            # Append the scraped summary if available
            summary = scraped_data.get(url, "No summary available.")
            final_output += f"**Summary:** {summary}\n\n"

    return final_output.strip()
