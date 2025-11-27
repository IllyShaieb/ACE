"""core: This module contains all the fundamental building blocks of ACE.

It is based on the principles of the MVP (Model-View-Presenter) architectural pattern.

### Model: `model.py`
This submodule is responsible for handling the data and business logic of the application.

### View: `view.py`
This submodule manages the user interface and presentation layer of the application.

### Presenter: `presenter.py`
This submodule acts as an intermediary between the Model and View, processing user input and
updating the UI accordingly.

### Additional Submodules
- `tools/`: Contains various utility functions and tools that support the core functionality of ACE.
- `constants.py`: Defines constant values used throughout the ACE application.
- `database.py`: Manages interactions with the database, including storing and retrieving data.
- `llm.py`: Handles interactions with large language models (LLMs) for natural language processing tasks.
"""

__version__ = "2024.12.0"
