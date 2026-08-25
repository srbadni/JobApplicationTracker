"""Media domain enums."""

from enum import StrEnum


class MediaCategory(StrEnum):
    """Business purpose of an uploaded file."""

    USER_AVATAR = "user_avatar"
    COMPANY_LOGO = "company_logo"
    RESUME = "resume"
    ATTACHMENT = "attachment"
