from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Company:
    """Framework-independent company representation."""

    id: int
    name: str
    persian_name: str
    province_id: int
    city_id: int
    activity_id: int
    personnel_count: str
    logo_path: str | None
    phone_number: str
    description: str | None = None
    website: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
