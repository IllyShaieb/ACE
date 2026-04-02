"""core.tools: Defines functional tools that ACE can use.

Each tool is a Python class that implements a specific function or capability. Tools must adhere to the
following requirements:
- The class name must end with "Tool".
- The class must have an `execute` method.
- The class must have a `name` attribute.
- The class must have a `description` attribute.
- The class must have a `parameters_schema` attribute.

Example tool class:
```python
class ExampleTool:
    @property
    def name(self):
        return "example"

    @property
    def description(self):
        return "An example tool that demonstrates the required structure."

    @property
    def parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "Input for the example tool."}
            },
            "required": ["input"]
        }

    def execute(self, input: str) -> str:
        return f"Example tool received: {input}"
```


### Dynamic Discovery (`discover_tools` function)
Tools can be dynamically discovered and instantiated by ACE at runtime, allowing for easy extensibility.
The `discover_tools` function scans the `core.tools` package for valid tool classes, imports them, and
instantiates them with any required services. This allows developers to add new tools simply by creating
new classes that follow the defined structure, without needing to modify existing code.
"""

import importlib
import inspect
import pkgutil
import sys
from typing import Any, Dict, List, Optional


def discover_tools(services: Optional[Dict[str, Any]] = None) -> List[Any]:
    """Dynamically discover and instantiate tool classes in the core.tools package."""
    tools = []
    services = services or {}

    # Identify the current package (core.tools) and its file path
    package_name = __name__
    package_path = sys.modules[__name__].__path__

    # Iterate over every .py file inside the core/tools directory
    for _, module_name, is_pkg in pkgutil.iter_modules(package_path):
        if is_pkg:
            continue  # Skip any sub-directories

        # Import the module dynamically (e.g., 'core.tools.weather')
        full_module_name = f"{package_name}.{module_name}"
        try:
            module = importlib.import_module(full_module_name)
        except ImportError as e:
            print(f"Failed to import tool module {full_module_name}: {e}")
            continue

        # Inspect the newly imported module for valid tool classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            is_tool = {
                "has_execute": hasattr(obj, "execute"),
                "name_ends_with_tool": name.endswith("Tool"),
                "has_name": hasattr(obj, "name"),
                "has_description": hasattr(obj, "description"),
                "has_parameters_schema": hasattr(obj, "parameters_schema"),
            }

            if all(is_tool.values()):
                try:
                    # Match required __init__ arguments to available services
                    signature = inspect.signature(obj)
                    required_params = [
                        p
                        for p in signature.parameters.values()
                        if p.default is inspect.Parameter.empty
                        and p.kind
                        in (
                            inspect.Parameter.POSITIONAL_ONLY,
                            inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            inspect.Parameter.KEYWORD_ONLY,
                        )
                    ]
                    if any(p.name not in services for p in required_params):
                        # Skip tools that require dependencies we do not currently have.
                        continue

                    init_args = {
                        p.name: services[p.name]
                        for p in signature.parameters.values()
                        if p.name in services
                    }
                    tools.append(obj(**init_args))
                except Exception as e:
                    print(f"Error instantiating tool '{name}': {e}")

    return tools
