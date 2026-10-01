from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String
)
from sqlalchemy.orm import relationship

from app.database import Base


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    leave_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    employee_id = Column(
        Integer,
        ForeignKey("employees.employee_id"),
        nullable=False
    )

    leave_type = Column(
        String(20),
        nullable=False
    )

    start_date = Column(
        Date,
        nullable=False
    )

    end_date = Column(
        Date,
        nullable=False
    )

    total_days = Column(
        Float,
        nullable=False
    )

    reason = Column(
        String(500),
        nullable=False
    )

    status = Column(
        String(20),
        default="Pending",
        nullable=False
    )

    approved_by = Column(
        Integer,
        nullable=True
    )

    rejection_reason = Column(
        String(500),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    employee = relationship(
        "Employee",
        back_populates="leave_requests"
    )