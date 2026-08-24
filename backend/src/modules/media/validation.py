"""Upload metadata and signature validation."""

import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .enums import MediaCategory
from .exceptions import MediaValidationError
from .policies import FileTypeRule, get_media_policy


class UploadCandidate(Protocol):
    """Subset of FastAPI's UploadFile used by the domain validator."""

    filename: str | None
    content_type: str | None
    size: int | None

    async def read(self, size: int = -1) -> bytes:
        """Read uploaded bytes."""
        ...

    async def seek(self, offset: int) -> None:
        """Move the upload cursor."""
        ...


@dataclass(frozen=True, slots=True)
class ValidatedUpload:
    """Trusted upload metadata derived from policy and file contents."""

    original_name: str
    extension: str
    mime_type: str
    max_size_bytes: int


async def validate_upload(category: MediaCategory, upload: UploadCandidate) -> ValidatedUpload:
    """Validate size metadata, extension, MIME declaration, and file signature."""
    policy = get_media_policy(category)
    original_name = sanitize_original_name(upload.filename)
    extension = Path(original_name).suffix.casefold()
    rule = policy.file_types.get(extension)

    if rule is None:
        allowed = ", ".join(sorted(policy.file_types))
        raise MediaValidationError(f"Unsupported file extension. Allowed extensions: {allowed}")

    if upload.size is not None and upload.size > policy.max_size_bytes:
        raise MediaValidationError(_size_error(policy.max_size_bytes))

    declared_mime = (upload.content_type or "application/octet-stream").split(";", maxsplit=1)[0].strip().casefold()
    if declared_mime not in rule.accepted_mime_types:
        raise MediaValidationError("The declared file type does not match the selected category")

    try:
        await upload.seek(0)
        header = await upload.read(1024)
        await upload.seek(0)
    except OSError as error:
        raise MediaValidationError("The uploaded file could not be read") from error

    if not _matches_signature(extension, rule, header):
        raise MediaValidationError("The file content does not match its filename extension")

    return ValidatedUpload(
        original_name=original_name,
        extension=extension,
        mime_type=rule.canonical_mime_type,
        max_size_bytes=policy.max_size_bytes,
    )


def sanitize_original_name(filename: str | None) -> str:
    """Keep a display-only basename and remove control/path characters."""
    if not filename:
        raise MediaValidationError("A filename is required")

    basename = filename.replace("\\", "/").rsplit("/", maxsplit=1)[-1]
    basename = unicodedata.normalize("NFC", basename)
    basename = "".join(character for character in basename if character.isprintable())
    basename = basename.strip().strip(".")

    if not basename:
        raise MediaValidationError("A valid filename is required")

    if len(basename) > 255:
        suffix = Path(basename).suffix
        basename = f"{Path(basename).stem[: 255 - len(suffix)]}{suffix}"
    return basename


def _matches_signature(extension: str, rule: FileTypeRule, header: bytes) -> bool:
    if extension == ".webp":
        return len(header) >= 12 and header.startswith(b"RIFF") and header[8:12] == b"WEBP"

    return any(header.startswith(signature) for signature in rule.signatures)


def _size_error(max_size_bytes: int) -> str:
    return f"File exceeds the {max_size_bytes // (1024 * 1024)} MiB limit for this category"
