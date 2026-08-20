from pydantic import BaseModel, Field, ConfigDict

from .enums import (
    EmploymentType,
    WorkMode,
    RelevantWorkExperience,
    MinimumEducationLevel,
    Gender,
    MilitaryServiceStatus,
)


class JobPostingRequest(BaseModel):
    job_title: str = Field(
        ...,
        min_length=1,
        max_length=150,
    )

    job_description: str = Field(
        ...,
        min_length=1,
    )

    company_overview: str = Field(
        ...,
        min_length=1,
    )

    employment_type: EmploymentType

    work_mode: WorkMode

    minimum_salary: int | None = Field(
        default=None,
        ge=0,
    )

    is_latin_text: bool

    work_experience: RelevantWorkExperience

    minimum_education: MinimumEducationLevel

    gender: Gender

    military_status: MilitaryServiceStatus

    post_notifications: bool = True


class JobPostingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int

    job_title: str
    job_description: str
    company_overview: str

    employment_type: EmploymentType
    work_mode: WorkMode

    minimum_salary: int | None
    is_latin_text: bool

    work_experience: RelevantWorkExperience
    minimum_education: MinimumEducationLevel
    gender: Gender
    military_status: MilitaryServiceStatus

    post_notifications: bool
