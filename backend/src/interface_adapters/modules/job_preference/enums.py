from enum import Enum


class PreferredEmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    REMOTE = "remote"
    INTERNSHIP = "internship"


class PreferredSeniorityLevel(str, Enum):
    ENTRY_LEVEL = "entry_level"
    SPECIALIST = "specialist"
    MANAGER = "manager"
    SENIOR_MANAGER = "senior_manager"


class PreferredJobBenefit(str, Enum):
    PROMOTION_OPPORTUNITY = "promotion_opportunity"
    INSURANCE = "insurance"
    TRAINING_COURSES = "training_courses"
    COMMUTING_SERVICE = "commuting_service"
    COMPANY_MEAL = "company_meal"
    FLEXIBLE_WORKING_HOURS = "flexible_working_hours"