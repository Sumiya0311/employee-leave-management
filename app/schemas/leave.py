from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LeaveCreate(BaseModel):
    employee_id: int = Field(..., gt=0)
    leave_type: str
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=2, max_length=500)

    @field_validator("leave_type")
    @classmethod
    def validate_leave_type(cls, value):
        allowed = {"Sick", "Casual", "Earned"}

        if value not in allowed:
            raise ValueError(
                "Leave type must be Sick, Casual, or Earned"
            )

        return value

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, value, info):
        start_date = info.data.get("start_date")

        if start_date and value < start_date:
            raise ValueError(
                "End date cannot be before start date"
            )

        if start_date and start_date < date.today():
            raise ValueError(
                "Leave cannot be applied for past dates"
            )

        return value


class LeaveResponse(BaseModel):
    leave_id: int
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    total_days: float
    reason: str
    status: str
    approved_by: int | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class LeaveRejectRequest(BaseModel):
    rejection_reason: str = Field(
        ...,
        min_length=2,
        max_length=500
    )