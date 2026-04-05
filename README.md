# ACE - Artificial Consciousness Engine

![GitHub Issues](https://img.shields.io/github/issues/illyshaieb/ACE)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/illyshaieb/ACE)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/illyshaieb/ACE)
![GitHub last commit](https://img.shields.io/github/last-commit/illyshaieb/ACE)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/illyshaieb/ACE)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/illyshaieb/ACE/total)


ACE is a digital assistant designed to help you with your daily tasks and provide you with answers to a variety of questions. ACE is designed to be easy to use, privacy-focused, and open-source, so you can customise it to suit your needs.

## Getting Started
ACE is built in Python Version 3.10, and uses the [uv](https://docs.astral.sh/uv/) package manager to manage dependencies.

### Installation
First, ensure you have Python 3.10 installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/).

Next, install the `uv` package manager by running the following command:

```bash
pip install uv
```

Then clone the ACE repository and navigate to the project directory:

```bash
git clone https://github.com/illyshaieb/ACE.git
cd ACE
```

Finally, install the dependencies for ACE by running the following command:

```bash
uv sync
```

### Setup
Before using ACE, you need to set up the following environment variables:
| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Your API key for accessing Google Gemini API (https://ai.google.dev/gemini-api/docs). |
| `OPENWEATHERMAP_API_KEY` | Your API key for the OpenWeatherMap API (https://openweathermap.org/api) to enable the WeatherTool. |
| `DEFAULT_LOCATION` | A default location (e.g., `London`) for the tools to use when no location is specified in a query. |
| `DEFAULT_TIMEZONE` | A default time-zone (e.g., `Europe/London`) for the tools to use when no time-zone is specified in a query. |

*These can be set in a `.env` file or exported as environment variables.*

### Running ACE
To start ACE, run the following command:

```bash
uv run main.py
```

This will start the ACE digital assistant, and you can interact with it by typing in commands and questions in a natural language format.

## Architecture
See the [Architecture Documentation](docs/ARCHITECTURE.md) for a detailed overview of how ACE works and its core components.

## Contributing
ACE is an open-source project, and contributions are welcome! Whether you want to report a bug or suggest a new feature, or even contribute code, your help is appreciated. Please read the [Contributing Guidelines](docs/CONTRIBUTING.md) for more information on how to get involved.

Also, please see the [Development Documentation](docs/DEVELOPMENT.md) for guidelines on developing new features and tools within the ACE framework.

## License
See the [LICENSE](LICENSE) file for information on the licensing of ACE.