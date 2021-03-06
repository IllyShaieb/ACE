from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Output(ABC):
    """
    The base class for all types of outputs.

    Provides a common interface for providing output to the user
    via any source of output.

    Attributes
    ----------
    prefix: str
        The prefix to display before the output.
    """

    prefix: str = None

    @abstractmethod
    def broadcast(self, message: str) -> None:
        """
        Send a message to the user via the output.
        """


class CommandLineOutput(Output):
    """
    Class for providing output to the user via a command line.

    Attributes
    ----------
    prefix: str
        The prefix to display before the output.
    """

    def broadcast(self, message: str) -> None:
        """
        Send a message to the user via the command line.
        """
        if self._prefix_empty():
            print(message)
        else:
            print(f"{self.prefix.rstrip()} {message}")

    def _prefix_empty(self) -> bool:
        """
        Determine if the prefix is empty.

        returns: True if the prefix is empty, False otherwise.
        """
        return not self.prefix or self.prefix.replace(" ", "") == ""
