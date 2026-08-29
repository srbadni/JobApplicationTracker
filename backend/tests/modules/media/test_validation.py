import io
import unittest

from src.interface_adapters.modules.media.enums import MediaCategory
from src.interface_adapters.modules.media.exceptions import MediaValidationError
from src.interface_adapters.modules.media.validation import validate_upload


class UploadStub:
    def __init__(
        self,
        content: bytes,
        *,
        filename: str,
        content_type: str,
        size: int | None = None,
    ) -> None:
        self._content = io.BytesIO(content)
        self.filename: str | None = filename
        self.content_type: str | None = content_type
        self.size: int | None = len(content) if size is None else size

    async def read(self, size: int = -1) -> bytes:
        return self._content.read(size)

    async def seek(self, offset: int) -> None:
        self._content.seek(offset)


class MediaValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_pdf_resume_is_validated_and_filename_is_reduced_to_basename(self) -> None:
        upload = UploadStub(
            b"%PDF-1.7\nresume",
            filename=r"C:\fakepath\resume.pdf",
            content_type="application/pdf",
        )

        validated = await validate_upload(MediaCategory.RESUME, upload)

        self.assertEqual(validated.original_name, "resume.pdf")
        self.assertEqual(validated.extension, ".pdf")
        self.assertEqual(validated.mime_type, "application/pdf")
        self.assertEqual(await upload.read(), b"%PDF-1.7\nresume")

    async def test_signature_must_match_extension(self) -> None:
        upload = UploadStub(
            b"not a pdf",
            filename="resume.pdf",
            content_type="application/pdf",
        )

        with self.assertRaises(MediaValidationError):
            await validate_upload(MediaCategory.RESUME, upload)

    async def test_resume_rejects_image_extensions(self) -> None:
        upload = UploadStub(
            b"\x89PNG\r\n\x1a\ncontent",
            filename="resume.png",
            content_type="image/png",
        )

        with self.assertRaises(MediaValidationError):
            await validate_upload(MediaCategory.RESUME, upload)

    async def test_size_metadata_is_checked_before_storage(self) -> None:
        upload = UploadStub(
            b"%PDF-1.7\nresume",
            filename="resume.pdf",
            content_type="application/pdf",
            size=6 * 1024 * 1024,
        )

        with self.assertRaises(MediaValidationError):
            await validate_upload(MediaCategory.RESUME, upload)
