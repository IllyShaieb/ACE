"""core: The core application engine for ACE.

This package is organised into distinct sub-packages, enforcing a strict separation  of concerns through
the Model-View-Presenter (MVP) architecture alongside modular  infrastructure components.

### Model-View-Presenter (MVP)
The core interaction loop is divided into three primary domains to ensure clear  boundaries and high
testability:
- `core.models`: Manages data state, LLM orchestration, and core business logic.
- `core.views`: Handles user interface rendering and input capture.
- `core.presenters`: Mediates the flow of information between models and views.

### Infrastructure & Capabilities
Supporting the MVP loop are isolated modules that handle external communication  and dynamic
functionality:
- `core.adapters`: Low-level execution layers for I/O, database, and HTTP connections.
- `core.services`: Orchestrates adapters to process data and handle specific workflows.
- `core.tools`: Independent, functional capabilities dynamically discoverable by the models.

### Design Principles
ACE utilises Dependency Injection to manage relationships between these components.

By injecting adapters into services, and services into tools and models, the system remains highly
flexible, allowing components to be easily swapped, extended, or mocked during testing.
"""
