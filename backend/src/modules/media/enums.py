from enum import StrEnum


class MediaCategory(StrEnum):
    """Supported business uses for uploaded files."""

    COMPANY_LOGO = "company_logo"
    USER_AVATAR = "user_avatar"
    RESUME = "resume"
    ATTACHMENT = "attachment"
