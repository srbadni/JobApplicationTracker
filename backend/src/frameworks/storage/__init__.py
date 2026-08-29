"""Swappable object-storage infrastructure."""

from .base import AsyncReadable, Storage, StoredObject
from .exceptions import InvalidStorageKeyError, StorageError, StorageLimitExceededError, StorageObjectNotFoundError
from .local import LocalStorage

__all__ = [
    "AsyncReadable",
    "InvalidStorageKeyError",
    "LocalStorage",
    "Storage",
    "StorageError",
    "StorageLimitExceededError",
    "StorageObjectNotFoundError",
    "StoredObject",
]
