from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
class EmployeeBase(BaseModel):
    employee_code: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr

    phone: str

    department_id: int = Field(
        ...,
        gt=0
    )

    designation: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    salary: float = Field(
        ...,
        gt=0
    )

    date_of_joining: date

    employment_type: str

    is_active: bool = True

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )
        return value

    @field_validator("date_of_joining")
    @classmethod
    def validate_joining_date(cls, value):
        if value > date.today():
            raise ValueError(
                "Date of joining cannot be in the future"
            )
        return value

    @field_validator("employment_type")
    @classmethod
    def validate_employment_type(cls, value):
        allowed_types = {
            "Full-Time",
            "Part-Time",
            "Intern",
            "Contract"
        }

        if value not in allowed_types:
            raise ValueError(
                "Employment type must be Full-Time, Part-Time, Intern, or Contract"
            )

        return value


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    employee_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )