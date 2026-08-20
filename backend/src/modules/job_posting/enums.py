from enum import Enum, StrEnum


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"


class WorkMode(StrEnum):
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"

class RelevantWorkExperience(StrEnum):
    NOT_IMPORTANT = "not_important"
    LESS_THAN_3_YEARS = "less_than_3_years"
    THREE_TO_SIX_YEARS = "three_to_six_years"
    MORE_THAN_6_YEARS = "more_than_6_years"


class MinimumEducationLevel(StrEnum):
    NOT_IMPORTANT = "not_important"
    DIPLOMA = "diploma"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"

class Gender(StrEnum):
    NOT_IMPORTANT = "not_important"
    MALE = "male"
    FEMALE = "female"

class MilitaryServiceStatus(StrEnum):
    NOT_IMPORTANT = "not_important"
    COMPLETED = "completed"
    EDUCATIONAL_EXEMPTION = "educational_exemption"
    PERMANENT_EXEMPTION = "permanent_exemption"