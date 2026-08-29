"""Local-filesystem implementation of the storage contract."""

import hashlib
import os
from collections.abc import AsyncIterator
from pathlib import Path
from uuid import uuid4

import anyio

from .base import AsyncReadable, StoredObject
from .exceptions import (
    InvalidStorageKeyError,
    StorageError,
    StorageLimitExceededError,
    StorageObjectNotFoundError,
)


class LocalStorage:
    """Persist opaque objects beneath one private filesystem root."""

    def __init__(self, root: str | Path, chunk_size_bytes: int = 1024 * 1024) -> None:
        if chunk_size_bytes <= 0:
            raise ValueError("chunk_size_bytes must be greater than zero")

        self.root = Path(root).expanduser().resolve()
        self.chunk_size_bytes = chunk_size_bytes
        self._initialized = False

    async def initialize(self) -> None:
        """Create and verify write access to the private storage root."""
        if self._initialized:
            return

        probe = self.root / f".storage-probe-{uuid4().hex}"
        try:
            await anyio.to_thread.run_sync(lambda: self.root.mkdir(parents=True, exist_ok=True))
            async with await anyio.open_file(probe, "xb"):
                pass
            await anyio.to_thread.run_sync(probe.unlink)
        except OSError as error:
            await _discard_file(probe)
            raise StorageError("Unable to initialize local storage") from error
        self._initialized = True

    async def save(
        self,
        *,
        key: str,
        source: AsyncReadable,
        max_size_bytes: int,
    ) -> StoredObject:
        if max_size_bytes <= 0:
            raise ValueError("max_size_bytes must be greater than zero")

        destination = self._resolve(key)
        temporary = destination.with_name(f".{destination.name}.{uuid4().hex}.part")
        checksum = hashlib.sha256()
        size_bytes = 0

        await self.initialize()
        await anyio.to_thread.run_sync(lambda: destination.parent.mkdir(parents=True, exist_ok=True))

        try:
            async with await anyio.open_file(temporary, "xb") as output:
                while chunk := await source.read(self.chunk_size_bytes):
                    size_bytes += len(chunk)
                    if size_bytes > max_size_bytes:
                        raise StorageLimitExceededError(max_size_bytes)

                    checksum.update(chunk)
                    await output.write(chunk)

                await output.flush()

            await anyio.to_thread.run_sync(os.replace, temporary, destination)
        except StorageLimitExceededError:
            await _discard_file(temporary)
            raise
        except OSError as error:
            await _discard_file(temporary)
            raise StorageError("Unable to persist the object in local storage") from error
        except Exception:
            await _discard_file(temporary)
            raise

        return StoredObject(size_bytes=size_bytes, checksum_sha256=checksum.hexdigest())

    async def delete(self, key: str) -> None:
        path = self._resolve(key)
        try:
            await anyio.to_thread.run_sync(lambda: path.unlink(missing_ok=True))
        except OSError as error:
            raise StorageError("Unable to delete the object from local storage") from error

    async def exists(self, key: str) -> bool:
        path = self._resolve(key)
        return await anyio.to_thread.run_sync(path.is_file)

    async def stream(self, key: str) -> AsyncIterator[bytes]:
        path = self._resolve(key)
        try:
            async with await anyio.open_file(path, "rb") as source:
                while chunk := await source.read(self.chunk_size_bytes):
                    yield chunk
        except FileNotFoundError as error:
            raise StorageObjectNotFoundError("Stored object was not found") from error
        except OSError as error:
            raise StorageError("Unable to read the object from local storage") from error

    def _resolve(self, key: str) -> Path:
        if not key or "\x00" in key:
            raise InvalidStorageKeyError("Storage key must not be empty")

        relative_path = Path(key)
        if relative_path.is_absolute():
            raise InvalidStorageKeyError("Absolute storage keys are not allowed")

        resolved = (self.root / relative_path).resolve()
        try:
            resolved.relative_to(self.root)
        except ValueError as error:
            raise InvalidStorageKeyError("Storage key escapes the configured root") from error

        if resolved == self.root:
            raise InvalidStorageKeyError("Storage key must identify an object")
        return resolved


async def _discard_file(path: Path) -> None:
    """Best-effort cleanup that never masks the original storage error."""
    try:
        await anyio.to_thread.run_sync(lambda: path.unlink(missing_ok=True))
    except OSError:
        pass
