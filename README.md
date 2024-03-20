<div align="center">

# ACE

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/illyshaieb/ACE/continuous_integration.yaml) ![GitHub repo size](https://img.shields.io/github/repo-size/illyshaieb/ace) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/4304d43af0004b7ba2e998565a1b31fb)](https://www.codacy.com/gh/IllyShaieb/ACE/dashboard?utm_source=github.com&utm_medium=referral&utm_content=illyshaieb/ACE&utm_campaign=Badge_Grade) [![made-with-python](https://img.shields.io/badge/made%20with-Python-1f425f.svg)](https://www.python.org/) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/illyshaieb/ace?color=yellow) ![GitHub last commit](https://img.shields.io/github/last-commit/illyshaieb/ace) ![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/illyshaieb/ace?color=white&label=latest%20release)

</div>

ACE, the Artificial Consciousness Engine, is a digital assistant. It is designed to help you with your daily tasks and keep you in the loop with your life and the world.

## Getting Started

### Prerequisites

Please make sure you have the following installed:

| Package    | Version | Description                       | Required           |
| ---------- | ------- | --------------------------------- | ------------------ |
| Python     | 3.9+    | https://www.python.org/downloads/ | :heavy_check_mark: |
| Poetry     | 1.0+    | https://python-poetry.org/        | :heavy_check_mark: |
| Git        | 2.27+   | https://git-scm.com/              | :heavy_check_mark: |
| Git LFS    | 3.4.1+  | https://git-lfs.github.com/       | :heavy_check_mark: |
| GitHub CLI | 2.7+    | https://github.com/cli/cli        | :x:                |

**Important Note:** This project uses Git Large File Storage (LFS) to manage large files. Please ensure you have Git LFS installed before cloning the repository.

### Installation

First, navigate to a directory of your choice and run one of the following commands:

- Git

  ```bash
  $ git clone https://github.com/IllyShaieb/ACE.git
  ```

- GitHub CLI

  ```shell
  $ gh clone IllyShaieb/ACE
  ```

Then run the following commands to install the dependencies:

```shell
$ cd ACE
$ poetry install
```

You must also ensure Git LFS is initialized. Run the following command to do so:

```shell
$ git lfs install
```

You must also install the following dependencies:

- [FFmpeg](https://ffmpeg.org/download.html):

  FFmpeg is a powerful multimedia framework that can handle almost any format of multimedia content, is highly portable, and can run across a wide range of operating systems and configurations

### Running

ACE can be run as a CLI (Command Line Interface) or as a GUI (Graphical User Interface).

To start ACE, run one of the following commands:

- CLI

  ```shell
  $ poetry run python main.py cli
  ```

- GUI

  ```shell
  $ poetry run python main.py gui
  ```

### Extending ACE

To extend ACE, please refer to the [Extending ACE](docs/EXTENDING_ACE.md) document. <!-- markdown-link-check-disable-line -->

## Features

|                | Intent           | Description                                                  | Example                      | Notes                                                                                              |
| -------------- | ---------------- | ------------------------------------------------------------ | ---------------------------- | -------------------------------------------------------------------------------------------------- |
| :wave:         | greeting         | respond with a greeting message                              | hello                        |                                                                                                    |
| :runner:       | goodbye          | respond with a goodbye message and then exit                 | goodbye                      |                                                                                                    |
| :computer:     | open_app         | open the specified application                               | open excel                   | **Only available on windows**                                                                      |
| :computer:     | close_app        | close the specified application                              | close notepad                | **Only available on windows**                                                                      |
| :partly_sunny: | current_weather  | get the current weather for a location                       | current weather in London    | **See [Weather](#weather) section for setup details**                                              |
| :partly_sunny: | tomorrow_weather | get tomorrow's weather for a location                        | tomorrow's weather in London | **See [Weather](#weather) section for setup details**                                              |
| :clipboard:    | show_todo_list   | show the count of items in the todo list, and the first item | show todo list               | **See [Todo List](#todo-list) section for setup details**                                          |
| :clipboard:    | add_todo         | add an item to the todo list                                 | add Task 1 to todo list      | This will add 'Task 1' to the todo list. **See [Todo List](#todo-list) section for setup details** |

## Weather

To set up the weather intent, you must set the following environment variables:
| Variable | Example | Description |
| --- | --- | --- |
| `ACE_HOME` | London | The default location for the weather intent, if no location is specified. |
| `ACE_WEATHER_KEY` | 822fc8446f5adc72ac8c766a871329a8 | The API key for the [OpenWeatherMap API](https://openweathermap.org/api) |

For Windows follow this link to set the environment variables:

- https://www.computerhope.com/issues/ch000549.htm

## Todo List

To set up the todo list intent, you must set the following environment variables:
| Variable | Example | Description |
| --- | --- | --- |
| `ACE_TODO_API_KEY` | 822fc8446f5adc72ac8c766a871329a8 | The API key for the [Todoist API](https://developer.todoist.com/sync/v9/) |

For Windows follow this link to set the environment variables:

- https://www.computerhope.com/issues/ch000549.htm
