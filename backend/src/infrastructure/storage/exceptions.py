"""Storage-layer exceptions."""


class StorageError(Exception):
    """Base error raised by a storage backend."""


class InvalidStorageKeyError(StorageError):
    """Raised when a key could escape the configured storage root."""


class StorageObjectNotFoundError(StorageError):
    """Raised when a requested object does not exist."""


class StorageLimitExceededError(StorageError):
    """Raised when a streamed upload exceeds its maximum allowed size."""

    def __init__(self, limit_bytes: int) -> None:
        self.limit_bytes = limit_bytes
        super().__init__(f"Object exceeds the {limit_bytes}-byte storage limit")
