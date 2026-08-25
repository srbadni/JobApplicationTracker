from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ..common.schemas import PersistentDeletion, TimestampSchema
from .enums import UserType


class UserBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    last_name: Annotated[str, Field(min_length=2, max_length=30, examples=["Userson"])]
    phone_number: Annotated[
        str | None,
        Field(
            pattern=r"^09\d{9}$",
            examples=["09123456789"],
            description="Iranian mobile number in 09XXXXXXXXX format",
        ),
    ] = None
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]


class User(TimestampSchema, UserBase, PersistentDeletion):
    """Complete user model with all fields."""

    hashed_password: str
    is_superuser: bool = False
    user_type: UserType = UserType.APPLICANT
    profile_image_url: Annotated[
        str,
        Field(
            default="https://www.profileimageurl.com",
            description="URL of the user's profile image",
        ),
    ]
    tier_id: int | None = None

    google_id: str | None = None
    github_id: str | None = None
    oauth_provider: str | None = None
    email_verified: bool = False
    oauth_created_at: datetime | None = None
    oauth_updated_at: datetime | None = None


class UserRead(BaseModel):
    """Schema for reading user data, excludes sensitive information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    last_name: Annotated[str, Field(min_length=2, max_length=30, examples=["Userson"])]
    phone_number: Annotated[
        str | None,
        Field(
            pattern=r"^09\d{9}$",
            examples=["09123456789"],
            description="Iranian mobile number in 09XXXXXXXXX format",
        ),
    ] = None
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]
    profile_image_url: str
    is_deleted: bool = False
    tier_id: int | None
    is_superuser: bool = False
    user_type: UserType
    email_verified: bool = False
    oauth_provider: str | None = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: Annotated[
        str,
        Field(
            min_length=8,
            description=(
                "Password must be at least 8 characters long and include a number,"
                "uppercase letter, lowercase letter, and special character"
            ),
            examples=["Str1ngst!"],
            pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
        ),
    ]
    google_id: str | None = None
    github_id: str | None = None
    oauth_provider: str | None = None
    email_verified: bool = False
    oauth_created_at: datetime | None = None
    oauth_updated_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class UserCreateInternal(UserBase):
    """Internal schema for user creation with hashed password."""

    hashed_password: str
    user_type: UserType = UserType.APPLICANT
    google_id: str | None = None
    github_id: str | None = None
    oauth_provider: str | None = None
    email_verified: bool = False
    oauth_created_at: datetime | None = None
    oauth_updated_at: datetime | None = None


class UserUpdate(BaseModel):
    """Schema for updating user data."""

    model_config = ConfigDict(extra="forbid")

    name: Annotated[
        str | None,
        Field(min_length=2, max_length=30, examples=["User Userberg"], default=None),
    ]
    last_name: Annotated[
        str | None,
        Field(min_length=2, max_length=30, examples=["Userberg"], default=None),
    ]
    phone_number: Annotated[
        str | None,
        Field(pattern=r"^09\d{9}$", examples=["09123456789"], default=None),
    ]
    email: Annotated[EmailStr | None, Field(examples=["user.userberg@example.com"], default=None)]
    profile_image_url: Annotated[
        str | None,
        Field(
            pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
            examples=["https://www.profileimageurl.com"],
            default=None,
        ),
    ]
    google_id: str | None = None
    github_id: str | None = None
    oauth_provider: str | None = None
    email_verified: bool | None = None
    oauth_updated_at: datetime | None = None


class UserUpdateInternal(UserUpdate):
    """Internal schema for user updates."""

    updated_at: datetime


class UserTierUpdate(BaseModel):
    """Schema for updating a user's tier."""

    tier_id: int


class UserDelete(BaseModel):
    """Schema for soft-deleting a user."""

    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


class UserAnonymize(BaseModel):
    """Schema for GDPR/LGPD compliant user anonymization.

    This schema includes all fields that need to be updated during
    the user anonymization process for privacy compliance.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    last_name: str
    phone_number: str | None = None
    hashed_password: str | None = None
    profile_image_url: str | None = None
    tier_id: int | None = None
    is_superuser: bool = False
    google_id: str | None = None
    github_id: str | None = None
    oauth_provider: str | None = None
    email_verified: bool = False
    oauth_created_at: datetime | None = None
    oauth_updated_at: datetime | None = None


class UserRestoreDeleted(BaseModel):
    """Schema for restoring a deleted user."""

    is_deleted: bool
