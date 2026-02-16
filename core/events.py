"""core.events: This module defines the classes for handling events that occur
in the ACE application, particularly those emitted by the view and handled by
the presenter.
"""

from typing import Callable, List


class Signal:
    """Handles the subscription and emission of events between the view and
    presenter."""

    def __init__(self):
        self._functions: List[Callable] = []

    def connect(self, func: Callable) -> None:
        """Connect a function to the signal.

        Args:
            func (Callable): The function to connect to the signal.

        Raises:
            TypeError: If the provided object is not callable.
        """
        if not callable(func):
            raise TypeError("Connected object must be callable")
        self._functions.append(func)

    def emit(self, event_data: str) -> None:
        """Emit an event to all connected functions.

        Args:
            event_data (str): The data associated with the event.
        """
        for func in self._functions:
            func(event_data)


class ViewEvents:
    """Defines the events that a view can emit to the presenter."""

    def __init__(self):
        self.on_user_input = Signal()
