import hashlib
import io
import tempfile
import unittest
from pathlib import Path

from src.infrastructure.storage import InvalidStorageKeyError, LocalStorage, StorageLimitExceededError


class AsyncBytesReader:
    def __init__(self, content: bytes) -> None:
        self._content = io.BytesIO(content)

    async def read(self, size: int = -1) -> bytes:
        return self._content.read(size)


class LocalStorageTests(unittest.IsolatedAsyncioTestCase):
    async def test_save_stream_and_delete(self) -> None:
        content = b"stored in chunks"
        with tempfile.TemporaryDirectory() as directory:
            storage = LocalStorage(directory, chunk_size_bytes=4)

            stored = await storage.save(
                key="opaque-key.pdf",
                source=AsyncBytesReader(content),
                max_size_bytes=100,
            )

            self.assertEqual(stored.size_bytes, len(content))
            self.assertEqual(stored.checksum_sha256, hashlib.sha256(content).hexdigest())
            self.assertTrue(await storage.exists("opaque-key.pdf"))

            streamed = b"".join([chunk async for chunk in storage.stream("opaque-key.pdf")])
            self.assertEqual(streamed, content)

            await storage.delete("opaque-key.pdf")
            self.assertFalse(await storage.exists("opaque-key.pdf"))

    async def test_oversized_upload_removes_partial_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            storage = LocalStorage(directory, chunk_size_bytes=4)

            with self.assertRaises(StorageLimitExceededError):
                await storage.save(
                    key="too-large.pdf",
                    source=AsyncBytesReader(b"123456789"),
                    max_size_bytes=8,
                )

            self.assertEqual(list(Path(directory).iterdir()), [])

    async def test_path_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            storage = LocalStorage(directory)

            with self.assertRaises(InvalidStorageKeyError):
                await storage.save(
                    key="../escaped.pdf",
                    source=AsyncBytesReader(b"content"),
                    max_size_bytes=100,
                )
