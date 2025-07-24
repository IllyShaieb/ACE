# ACE

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

## Usage

To start ACE, run the following command:

```bash
uv run main.py
```

This will start the ACE digital assistant, and you can interact with it by typing in commands and questions in a natural language format.

## How ACE Works

The "brain" of the application is the `ACEModel`, located in `core/model.py`. Its main job is to understand what a user says and decide what actions the application should take in response. It doesn't _do_ the actions, it just identifies them.

The class works in three main stages:

### 1. Initialisation (`__init__`)

When an `ACEModel` is created, it loads a pre-trained English language model from the `spacy` library and sets up a `Matcher` tool. This tool is used to find specific words and phrases based on rules we define.

### 2. Defining Intents (`_define_intents`)

This method is the "rulebook" for our model. It contains a list of **intents**—concepts the bot can recognize. Each intent has:

- **Patterns**: The specific words or phrases to look for (e.g., `who are you`).
- **Action**: The command to execute if the pattern is found (e.g., `IDENTIFY`).
- **Priority**: A score for how important the intent is. Specific questions have a higher priority than simple greetings.

### 3. Processing Input (`__call__`)

When the user types something, the model processes it like this:

1.  **Find All Matches**: It finds every pattern that exists in the user's input.
2.  **Filter for Importance**: It checks if any of the matched intents are "important" (i.e., have a priority score greater than 1).
    - If yes, it **discards all the low-priority "conversational" intents** (like greetings). This allows the model to focus on the user's actual questions or commands.
    - If no important intents are found, it proceeds with the conversational ones.
3.  **Order Actions**: It sorts the final list of actions based on where they appeared in the user's sentence. This ensures the response feels natural and follows the user's line of questioning.
4.  **Return Actions**: It returns a clean, ordered list of action commands (e.g., `['GREETING', 'IDENTITY']`) to the Presenter, which is responsible for executing them.

## Contributing

This section is under development. Contributions are welcome, and we will provide more details soon. Keep an eye on this space!

## License

This section is under development. The license details will be provided soon. Stay tuned!

## Contact

Feel free to reach out to me on [GitHub](shaiebilly+ace@gmail.com) if you have any questions or feedback about ACE. I would love to hear from you!
