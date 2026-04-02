"""core.adapters: Manages external connections and I/O for the ACE application.

Adapters handle the technical details of interacting with outside systems—such as
making HTTP requests, executing database queries, or managing terminal input.

They fetch and deliver raw data, but contain no application-specific business logic.
"""

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
