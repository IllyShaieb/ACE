# ACE

### Contents

| Section                       | Description                                  |
|-------------------------------|----------------------------------------------|
| 🚀 [Introduction](#introduction)                | Overview of ACE and its features             |
| 🛠️ [Installation](#installation)                | Steps to install ACE and dependencies        |
| ⚙️ [Setup](#setup)                              | Environment variable configuration           |
| 💡 [Usage](#usage)                              | How to run and interact with ACE             |
| 🧠 [How ACE Works](#how-ace-works)              | Explanation of ACE's internal logic          |
| 🧩 [Adding New Tools](#adding-new-tools) | Guide to extending ACE with custom tools |

## Introduction

Welcome to ACE (Artificial Consciousness Engine), which is a digital assistant designed to help you with your daily tasks and provide you with answers to a variety of questions. ACE is designed to be easy to use, privacy-focused, and open-source, so you can customise it to suit your needs.

## Installation

ACE is built in Python Version 3.10, and uses the [uv](https://docs.astral.sh/uv/) package manager to manage dependencies.

First, ensure you have Python 3.10 installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/).

Next, install the `uv` package manager by running the following command:

```bash
pip install uv
```

Finally, install the dependencies for ACE by running the following command:

```bash
uv sync
```

## Setup
Before using ACE, you need to set up the following environment variables:
| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Your API key for accessing Google Gemini API (https://ai.google.dev/gemini-api/docs). |
| `OPENWEATHERMAP_API_KEY` | Your API key for the OpenWeatherMap API (https://openweathermap.org/api) to enable the WeatherTool. |
| `DEFAULT_LOCATION` | A default location (e.g., `London`) for the tools to use when no location is specified in a query. |
| `DEFAULT_TIMEZONE` | A default time-zone (e.g., `Europe/London`) for the tools to use when no time-zone is specified in a query. |

*These can be set in a `.env` file or exported as environment variables.*

## Usage

To start ACE, run the following command:

```bash
uv run main.py
```

This will start the ACE digital assistant, and you can interact with it by typing in commands and questions in a natural language format.

## How ACE Works

ACE operates using a modern Large Language Model (LLM) architecture with Tool-Calling capabilities, allowing it to move beyond simple chat and perform complex, real-world actions.

1. **Receives the Query & Context:** You submit a prompt (e.g., "What is the time right now?"). The LLM reads your request along with the entire prior conversation history (the context) to understand your intent.

2. **Intelligent Tool Selection:** The LLM automatically determines if one of the application's available Tools is required. For the time query, it identifies the `get_date_time` tool and extracts any relevant parameters.

3. **Executes the Action:** The system momentarily pauses the chat to call the corresponding Tool class's `execute()` method (e.g., `ClockTool().execute(format="time")`), capturing the raw result.

4. **Formulates and Delivers the Answer:** The raw tool output is sent back to the LLM, which then processes it and formats it into a polite, polished, and persona-aligned response for display in your interface.

## Core Components

| Component               | Role                                  |
|-------------------------|----------------------------------------------|
| `main.py`               | The main **Entry Point**. Wires the concrete components together via Dependency Injection and starts the application. |
| `core/models.py`        | The **Intelligence Layer**. Contains `GeminiIntelligenceModel` (powered by the Gemini API) and the simpler `MinimumViableModel`. Implements the three-pass tool-calling loop: Intent → Execution → Synthesis. |
| `core/views.py`         | The **User Interface**. Contains `ConsoleView` (the console frontend) and `BuiltinIOAdapter` (wraps Python's built-in I/O). |
| `core/presenters.py`    | The **Orchestrator**. `ConsolePresenter` mediates between the View and the Model, reacting to view events and driving the application loop. |
| `core/protocols.py`     | The **Contract Layer**. Defines `Protocol` interfaces (`ModelProtocol`, `ViewProtocol`, `IOAdapterProtocol`, `ToolProtocol`, etc.) that decouple components and enable Dependency Injection. |
| `core/tools.py`         | The **Tool Registry**. Defines class-based Tools (e.g., `ClockTool`, `CharacterCounterTool`, `CoinFlipTool`) that the LLM can invoke. Tools are auto-discovered by `discover_tools()`. |
| `core/events.py`        | The **Event Bus**. Provides the `Signal` class and `ViewEvents` dataclass for decoupled, event-driven communication between the View and Presenter. |

## Adding New Tools

Adding a new tool is straightforward. Tools are class-based and automatically discovered at startup by `discover_tools()` — no registration or wiring needed.

1. **Open `core/tools.py`**.
2. **Create a new class** that satisfies the `ToolProtocol` interface by implementing three properties and one method:
    - `name` (str property): The unique tool name the LLM will reference.
    - `description` (str property): A brief description of what the tool does. This helps the LLM understand when to use it.
    - `parameters_schema` (dict property): A JSON-schema-style dict describing the tool's parameters.
    - `execute(**kwargs)`: The method that performs the tool's action and returns its result.

### Example:

```python
import random
from typing import Any, Dict

class RandomNumberTool:
    """A tool that generates a random integer between two values."""

    @property
    def name(self) -> str:
        return "generate_random_number"

    @property
    def description(self) -> str:
        return "Generates a random integer between min_value and max_value (inclusive)."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "OBJECT",
            "properties": {
                "min_value": {"type": "INTEGER", "description": "The minimum value."},
                "max_value": {"type": "INTEGER", "description": "The maximum value."},
            },
            "required": ["min_value", "max_value"],
        }

    def execute(self, min_value: int, max_value: int, **kwargs: Any) -> int:
        """Return a random integer between min_value and max_value."""
        return random.randint(min_value, max_value)
```

### How Auto-Discovery Works

`discover_tools()` in `core/tools.py` uses `inspect` to scan the module at startup. Any class that meets ALL of the following criteria will be automatically instantiated and passed to the model:

1. Has a class name ending with the word `"Tool"` (e.g., `WeatherTool`).
2. Has a callable `execute` method.
3. Has a `name` property.
4. Has a `description` property.
5. Has a `parameters_schema` property.

*Note: The metadata attributes (`name`, `description`, `parameters_schema`) MUST be defined as class variables or `@property` decorators so the auto-discovery engine can read them before instantiation. Do not define them as instance variables inside `__init__`.*

There is no manual registration step.

### Testing Your Tool

Add a test for your new tool in [`tests/test_tools.py`](tests/test_tools.py):

```python
class TestRandomNumberTool(unittest.TestCase):
    """Tests for the RandomNumberTool."""

    def setUp(self):
        self.tool = tools.RandomNumberTool()

    def test_execute_returns_integer_in_range(self):
        """Ensure execute() returns an integer within the specified range."""
        result = self.tool.execute(min_value=1, max_value=10)
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 1)
        self.assertLessEqual(result, 10)
```

This ensures your tool is correctly implemented and callable.

## Contributing

This section is under development. Contributions are welcome, and we will provide more details soon. Keep an eye on this space!

## License

This section is under development. The license details will be provided soon. Stay tuned!

## Contact

Feel free to reach out to me via [email](mailto:shaiebilly+ace@gmail.com) if you have any questions or feedback about ACE. I would love to hear from you!
