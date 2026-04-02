"""core.adapters: This module defines adapters for the ACE application, providing
a layer of abstraction for different APIs the tools might depend on."""

from .http import RequestsHTTPAdapter
from .io import BuiltinIOAdapter, RichIOAdapter
from .storage import DatabaseConversationStorageAdapter, DatabaseLogStorageAdapter

__all__ = [
    "BuiltinIOAdapter",
    "RichIOAdapter",
    "RequestsHTTPAdapter",
    "DatabaseConversationStorageAdapter",
    "DatabaseLogStorageAdapter",
]
