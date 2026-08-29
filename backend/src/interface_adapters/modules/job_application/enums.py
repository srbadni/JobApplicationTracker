from enum import StrEnum


class ApplicationStatus(StrEnum):
    SENT_TO_EMPLOYER = "sent_to_employer"
    REVIEWED = "reviewed"
    INTERVIEW = "interview"
    HIRED = "hired"
    OTHER = "other"