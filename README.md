# ACE

ACE, the Artificial Consciousness Engine, is a digital assistant. It is designed to help you with your daily tasks and keep you in the loop with your life and the world.

## Getting Started

These instructions will get you up and running with ACE on your local machine.

### Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)

_Note: This project is developed and tested on Python 3.10.2, in Windows 10. It may work on other versions and operating systems, but it is not guaranteed._

### Installing

1.  Clone the repository:

    ```bash
    git clone https://github.com/IllyShaieb/ACE.git
    ```

2.  Create a virtual environment (optional but recommended):

    ```bash
    python -m venv .venv
    ```

3.  Activate the virtual environment:

    ```bash
    # On Windows
    .venv\Scripts\activate
    ```

4.  Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5.  Create a `.env` file in the root directory of the project and add the following environment variables:

    ```env
    ACE_WEATHER_API_KEY=your_api_key_here
    ACE_HOME_LOCATION=your_home_location_here
    ACE_TODO_MANAGER=todoist
    ACE_TODO_MANAGER_API_KEY=your_api_key_here
    ACE_NEWS_API_KEY=your_api_key_here
    ACE_NEWS_SOURCES=your_news_sources_here (comma-separated)
    ACE_LOGGING_LEVEL=INFO
    ```

See the [Setting up APIs and Skills](#setting-up-apis-and-skills) section for more information on setting up the APIs.

### Running ACE

1.  Make sure your virtual environment is activated.
2.  Run the main script:

    ```bash
    python main.py
    ```

## Usage

### Interacting with ACE

Once you run `main.py`, you can interact with ACE by typing your requests in the console. ACE will try to understand your intent and respond accordingly.

### Available Skills

ACE currently has the following skills:

- **Basic Interactions:**

  - Greetings: (e.g., "hello", "good morning")
  - Farewells (e.g., "goodbye", "bye")
  - Self-introduction (e.g., "who are you?")
  - Responding to "how are you?"

- **Weather:**

  - Get the current weather for a location (e.g., "what's the weather in London?")
  - Get tomorrow's weather for a location (e.g., "what's the weather in New York tomorrow?")

- **To-Do List:**

  - Show today's tasks (e.g., "show my to-dos")
  - Add a task to the to-do list (e.g., "add buy groceries to my to-do list")

- **Time:**

  - Tell the current time (e.g., "what time is it?")
  - Calculate future time (e.g., "what will the time be in 2 hours?")

- **News:**
  - Get the latest news (e.g., "what's the news?")
  - Get news from a specific topic (e.g., "what's in the news about technology?")

## Setting up APIs and Skills

ACE uses external APIs and services to provide some of its functionality. You'll need to set up accounts and configure the following:

- **Weather:**
  _Note: ACE uses WeatherAPI to get weather data._

  1.  Sign up for a free account at [WeatherAPI](https://www.weatherapi.com/).
  2.  Obtain your API key from the WeatherAPI dashboard.
  3.  In your `.env` file:
      - Set the `ACE_WEATHER_API_KEY` variable to your WeatherAPI key.
      - Set the `ACE_HOME_LOCATION` variable to your home location (e.g., "London").

- **To-Do List:**
  _Note: Currently, ACE only supports ToDoist as the to-do list manager._

  1.  Sign up for a [ToDoist](https://todoist.com/) account if you don't already have one.
  2.  Go to [ToDoist Developers](https://developer.todoist.com/) and create an app to obtain your API key.
  3.  In your `.env` file:
      - Set the `ACE_TODO_MANAGER` variable to `todoist`.
      - Set the `ACE_TODO_MANAGER_API_KEY` variable to your ToDoist API key.

- **News:**
  _Note: ACE uses the NewsAPI to get news data._

  1.  Sign up for a free account at [NewsAPI](https://newsapi.org/).
  2.  Obtain your API key from the NewsAPI dashboard.
  3.  In your `.env` file:
      - Set the `ACE_NEWS_API_KEY` variable to your NewsAPI key.
      - Set the `ACE_NEWS_SOURCES` variable to the news sources you want to get news from (e.g., "bbc-news, cnn").

- **Logging:**

  _Note: You can control the logging level of ACE by setting the `ACE_LOGGING_LEVEL` variable in your `.env` file._

  - Set the `ACE_LOGGING_LEVEL` variable to the desired logging level to control the verbosity of the logs (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
  - Logs will be written to the `ace_<YYYY-MM-DD>.log` file in the `logs` directory, where `<YYYY-MM-DD>` is the current date.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [CalVer](https://calver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/IllyShaieb/ACE/tags).

## Authors

- **Illy Shaieb** - [IllyShaieb](https://github.com/IllyShaieb)

## License

This project is licensed under the GNU General Public License version 3 (GPLv3) - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

We have used the following resources to build ACE:

- [WeatherAPI](https://www.weatherapi.com/) - For weather data
- [Todoist API](https://developer.todoist.com/rest/v2/) - For managing to-do lists
- [NewsAPI](https://newsapi.org/) - For news data
