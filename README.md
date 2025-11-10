# ACE

### Contents

| Section                       | Description                                  |
|-------------------------------|----------------------------------------------|
| 🚀 [Introduction](#introduction)                | Overview of ACE and its features             |
| 🛠️ [Installation](#installation)                | Steps to install ACE and dependencies        |
| ⚙️ [Setup](#setup)                              | Environment variable configuration           |
| 💡 [Usage](#usage)                              | How to run and interact with ACE             |
| 🧠 [How ACE Works](#how-ace-works)              | Explanation of ACE's internal logic          |
| 🧩 [Adding New Action Handlers](#adding-new-action-handlers) | Guide to extending ACE with custom actions |

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
uv install
```

## Setup
Before using ACE, you need to set up the following environment variables:
- `WEATHER_API_KEY`: Your API key for accessing weather data (https://www.weatherapi.com/).
- `ACE_MODE_OVERRIDE`: Set to `1` to force GUI mode, `2` to force Console mode, or `0` to prompt the user each time at startup.
- `GEMINI_API_KEY`: Your API key for accessing Google Gemini API (https://ai.google.dev/gemini-api/docs).

*This can be set in a `.env` file or exported as an environment variable.*

## Usage

To start ACE, run the following command:

```bash
uv run main.py
```

This will start the ACE digital assistant, and you can interact with it by typing in commands and questions in a natural language format.

## How ACE Works

ACE operates using a modern Large Language Model (LLM) architecture with Tool-Calling capabilities, allowing it to move beyond simple chat and perform complex, real-world actions.

1. **Receives the Query & Context:** You submit a prompt (e.g., "What is the weather in London?"). The LLM reads your request along with the entire prior conversation history (the context) to understand your intent.

2. **Intelligent Tool Selection:** The LLM, acting as a superb interpreter, automatically determines if one of the application’s available Python functions—which we call "Tools"—is required. For the weather, it identifies the get_weather tool and extracts the necessary parameter ("London").

3. **Executes the Action:** The system momentarily pauses the chat to execute the actual Python function (core.actions.handle_get_weather(location="London")), capturing the raw result (e.g., "15°C, partly cloudy").

4. **Formulates and Delivers the Answer:** The raw tool output is sent back to the LLM, which then processes it and formats it into a polite, polished, and persona-aligned response for display in your interface.

## Core Components

| Component               | Role                                  |
|-------------------------|----------------------------------------------|
| `main.py`               | The main **Entry Point**. It initialises the selected View, Model, and Presenter.         |
| `core/model.py`         | The Model Interface. A thin wrapper that provides a consistent interface to the LLM API's capabilities. |
| `core/view.py`            | The **User Interface** (IACEView protocol). Contains the `ConsoleView` and `DesktopView` (customtkinter) frontends.    |
| `core/presenter.py`    | The **Orchestrator** (Model-View-Presenter logic). It manages the application loop, loads chat history, and coordinates the flow between the View and the Model. |
| `core/llm.py`          | The **API Gateway**. Handles all direct interaction with the Gemini LLM, defining the LLM's available Tools and executing tool-calls. |
| `core/actions.py`      | The **Tool Registry**. Defines all extensible Python functions (Tools) that the LLM can be instructed to invoke. |
| `core/database.py`   | The **Data Store**. Manages all SQLite database operations for persistently recording conversations. |

## Adding New Actions (Tools)

Adding new tools extremely simple:

1.  **Open `core/actions.py`**.
2.  **Create your Python function**. Make sure it has typed arguments.
3.  **Add the decorator** `@register_handler` above your function, providing the following parameters:
    - `action_name` (str): The unique name of the action.
    - `description` (str): A brief description of what the action does. This helps the LLM understand when to use it.
    - `requires_input` (bool, optional): Whether the action requires user input. Defaults to `False`.

### Example:

```python
import random

@register_handler("RANDOM_NUMBER", description="Generates a random number between two integers.", requires_input=True)
def generate_random_number(min_value: int, max_value: int) -> int:
    """Generates a random number between min_value and max_value."""
    return random.randint(min_value, max_value)
```

### Technical Note: The Action Handler Registry

The `@register_handler` decorator automatically stores your function in the central `ACTION_HANDLERS` dictionary as an `ActionHandler` object. If a handler is registered with a name that already exists, the new function will automatically override the original. A warning is issued to the developer when this occurs, permitting advanced features like intentional patching or local testing overrides.

**Best practice:** Use unique action names unless you intentionally want to override an existing handler (e.g., in tests or plugins).

**Example of overriding:**

```python
@register_handler("MY_ACTION", description="First version of MY_ACTION")
def first_handler():
    return "First version"

# This will override the previous handler for "MY_ACTION"
@register_handler("MY_ACTION", description="Second version of MY_ACTION")
def second_handler():
    return "Second version"

# Now, execute_action("MY_ACTION") will return "Second version"
```

### Testing Your Handler

Add a test for your new handler in [`tests/test_actions.py`](tests/test_actions.py):

```python
class TestMyCustomAction(unittest.TestCase):
    """Tests for the MY_CUSTOM_ACTION handler."""

    def test_handle_my_custom_action(self):
        """Ensure the MY_CUSTOM_ACTION handler returns the expected response."""
        result = actions.execute_action("MY_CUSTOM_ACTION")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "This is my custom action response!")
```

This ensures your handler is registered and works as expected.

## Contributing

This section is under development. Contributions are welcome, and we will provide more details soon. Keep an eye on this space!

## License

This section is under development. The license details will be provided soon. Stay tuned!

## Contact

Feel free to reach out to me on [GitHub](shaiebilly+ace@gmail.com) if you have any questions or feedback about ACE. I would love to hear from you!
