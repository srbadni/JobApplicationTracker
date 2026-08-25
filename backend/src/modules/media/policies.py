"""Per-category upload policies."""

from dataclasses import dataclass

from .enums import MediaCategory

MEBIBYTE = 1024 * 1024


@dataclass(frozen=True, slots=True)
class FileTypeRule:
    """Allowed metadata and signature for one filename extension."""

    canonical_mime_type: str
    accepted_mime_types: frozenset[str]
    signatures: tuple[bytes, ...]


@dataclass(frozen=True, slots=True)
class MediaPolicy:
    """Maximum size and file types accepted for a media category."""

    max_size_bytes: int
    file_types: dict[str, FileTypeRule]


PDF = FileTypeRule(
    canonical_mime_type="application/pdf",
    accepted_mime_types=frozenset({"application/pdf", "application/octet-stream"}),
    signatures=(b"%PDF-",),
)
DOC = FileTypeRule(
    canonical_mime_type="application/msword",
    accepted_mime_types=frozenset(
        {
            "application/msword",
            "application/octet-stream",
            "application/x-ole-storage",
        }
    ),
    signatures=(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
)
DOCX = FileTypeRule(
    canonical_mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    accepted_mime_types=frozenset(
        {
            "application/octet-stream",
            "application/zip",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
    ),
    signatures=(b"PK\x03\x04",),
)
JPEG = FileTypeRule(
    canonical_mime_type="image/jpeg",
    accepted_mime_types=frozenset({"application/octet-stream", "image/jpeg", "image/jpg"}),
    signatures=(b"\xff\xd8\xff",),
)
PNG = FileTypeRule(
    canonical_mime_type="image/png",
    accepted_mime_types=frozenset({"application/octet-stream", "image/png"}),
    signatures=(b"\x89PNG\r\n\x1a\n",),
)
WEBP = FileTypeRule(
    canonical_mime_type="image/webp",
    accepted_mime_types=frozenset({"application/octet-stream", "image/webp"}),
    signatures=(b"RIFF",),
)

DOCUMENT_TYPES = {
    ".doc": DOC,
    ".docx": DOCX,
    ".pdf": PDF,
}
IMAGE_TYPES = {
    ".jpeg": JPEG,
    ".jpg": JPEG,
    ".png": PNG,
    ".webp": WEBP,
}

MEDIA_POLICIES: dict[MediaCategory, MediaPolicy] = {
    MediaCategory.USER_AVATAR: MediaPolicy(max_size_bytes=2 * MEBIBYTE, file_types=IMAGE_TYPES),
    MediaCategory.COMPANY_LOGO: MediaPolicy(max_size_bytes=2 * MEBIBYTE, file_types=IMAGE_TYPES),
    MediaCategory.RESUME: MediaPolicy(max_size_bytes=5 * MEBIBYTE, file_types=DOCUMENT_TYPES),
    MediaCategory.ATTACHMENT: MediaPolicy(
        max_size_bytes=10 * MEBIBYTE,
        file_types={**DOCUMENT_TYPES, **IMAGE_TYPES},
    ),
}


def get_media_policy(category: MediaCategory) -> MediaPolicy:
    """Return the immutable policy selected by a category."""
    return MEDIA_POLICIES[category]
