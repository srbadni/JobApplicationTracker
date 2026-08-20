"""Authentication HTTP exception re-exports used by the application."""

from fastapi.exceptions import HTTPException
from fastcrud.exceptions.http_exceptions import (
    BadRequestException,
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
    RateLimitException,
    UnauthorizedException,
    UnprocessableEntityException,
)

__all__ = [
    "BadRequestException",
    "NotFoundException",
    "ForbiddenException",
    "UnauthorizedException",
    "UnprocessableEntityException",
    "DuplicateValueException",
    "RateLimitException",
    "HTTPException",
]
