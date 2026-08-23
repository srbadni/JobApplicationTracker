from abc import ABC, abstractmethod
from collections.abc import AsyncIterable


class Storage(ABC):
    """Backend-independent contract for private file storage."""

    @abstractmethod
    async def save(self, storage_key: str, content: AsyncIterable[bytes]) -> int:
        """Store content and return the number of bytes written."""

    @abstractmethod
    async def delete(self, storage_key: str) -> None:
        """Delete content when it exists."""

    @abstractmethod
    async def read(self, storage_key: str) -> bytes:
        """Read private content after authorization has been performed."""
