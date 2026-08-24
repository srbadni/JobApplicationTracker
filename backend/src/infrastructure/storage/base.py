"""Backend-independent storage contracts."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol


class AsyncReadable(Protocol):
    """The minimal async stream interface required by storage backends."""

    async def read(self, size: int = -1) -> bytes:
        """Read up to ``size`` bytes from the stream."""
        ...


@dataclass(frozen=True, slots=True)
class StoredObject:
    """Metadata calculated while an object is persisted."""

    size_bytes: int
    checksum_sha256: str


class Storage(Protocol):
    """Contract implemented by local and future remote object stores."""

    async def initialize(self) -> None:
        """Prepare the backend and fail early when it is unavailable."""
        ...

    async def save(
        self,
        *,
        key: str,
        source: AsyncReadable,
        max_size_bytes: int,
    ) -> StoredObject:
        """Persist ``source`` under an opaque key."""
        ...

    async def delete(self, key: str) -> None:
        """Delete an object if it exists."""
        ...

    async def exists(self, key: str) -> bool:
        """Return whether an object exists."""
        ...

    def stream(self, key: str) -> AsyncIterator[bytes]:
        """Stream an object's bytes without loading it all into memory."""
        ...
