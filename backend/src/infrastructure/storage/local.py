import asyncio
from collections.abc import AsyncIterable
from pathlib import Path

from .base import Storage


class LocalStorage(Storage):
    """Store files beneath a configured local directory."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    def _path_for(self, storage_key: str) -> Path:
        path = (self.root / storage_key).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("storage_key must stay within the storage root")
        return path

    async def save(self, storage_key: str, content: AsyncIterable[bytes]) -> int:
        path = self._path_for(storage_key)
        await asyncio.to_thread(path.parent.mkdir, parents=True, exist_ok=True)
        size = 0
        with path.open("xb") as destination:
            async for chunk in content:
                size += len(chunk)
                await asyncio.to_thread(destination.write, chunk)
        return size

    async def delete(self, storage_key: str) -> None:
        path = self._path_for(storage_key)
        try:
            await asyncio.to_thread(path.unlink)
        except FileNotFoundError:
            pass

    async def read(self, storage_key: str) -> bytes:
        return await asyncio.to_thread(self._path_for(storage_key).read_bytes)
