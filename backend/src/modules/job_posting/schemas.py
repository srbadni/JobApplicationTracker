from pydantic import BaseModel, ConfigDict, Field

from .enums import (
    EmploymentType,
    Gender,
    MilitaryServiceStatus,
    MinimumEducationLevel,
    RelevantWorkExperience,
    WorkMode,
)


class JobPostingCreate(BaseModel):
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

    job_category_id: int = Field()
    province_id: int = Field()
    city_id: int = Field()
    salary_range_id: int = Field()

    employment_type: EmploymentType

    work_mode: WorkMode

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
    job_category_id: int
    province_id: int
    salary_range_id: int
    city_id: int

    job_title: str
    job_description: str
    company_overview: str

    employment_type: EmploymentType
    work_mode: WorkMode

    is_latin_text: bool

    work_experience: RelevantWorkExperience
    minimum_education: MinimumEducationLevel
    gender: Gender
    military_status: MilitaryServiceStatus

    post_notifications: bool
