import pytest
from pydantic import ValidationError

from src.modules.company_membership.schemas import EmployerRegistrationCreate


def valid_payload() -> dict:
    return {
        "user": {
            "name": "Ada Employer",
            "phone_number": "09123456789",
            "email": "ada@example.com",
            "password": "Password123!",
        },
        "company": {
            "name": "  Analytical Engines  ",
            "website": "https://example.com",
        },
    }


def test_employer_registration_validates_both_form_steps() -> None:
    registration = EmployerRegistrationCreate.model_validate(valid_payload())

    assert registration.user.email == "ada@example.com"
    assert registration.company.name == "Analytical Engines"


@pytest.mark.parametrize("missing_section", ["user", "company"])
def test_employer_registration_requires_both_sections(missing_section: str) -> None:
    payload = valid_payload()
    del payload[missing_section]

    with pytest.raises(ValidationError):
        EmployerRegistrationCreate.model_validate(payload)
