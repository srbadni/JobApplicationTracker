from pydantic import BaseModel, ConfigDict, model_validator


class SalaryRangeCreate(BaseModel):
    title: str
    min_salary: int | None = None
    max_salary: int | None = None

    @model_validator(mode="after")
    def validate_salary_bounds(self):
        if self.min_salary is not None and self.max_salary is not None and self.min_salary > self.max_salary:
            raise ValueError("min_salary must be less than or equal to max_salary")
        return self


class SalaryRangeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    min_salary: int | None
    max_salary: int | None
