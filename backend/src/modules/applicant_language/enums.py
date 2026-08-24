from enum import Enum


class LanguageLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    PROFESSIONAL = "professional"
    NATIVE = "native"