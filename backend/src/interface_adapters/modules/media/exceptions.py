"""Media-specific domain errors."""

from ..common.exceptions import DomainError, PermissionDeniedError, ResourceNotFoundError, ValidationError


class MediaNotFoundError(ResourceNotFoundError):
    """Raised when a media record does not exist."""


class MediaValidationError(ValidationError):
    """Raised when an upload violates its category policy."""


class MediaAccessDeniedError(PermissionDeniedError):
    """Raised when a user cannot access a media object."""


class MediaStorageError(DomainError):
    """Raised when persisted media bytes are unavailable."""
