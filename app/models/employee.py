from datetime import datetime

from sqlalchemy import (
    Boolean,
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


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True)

    employee_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    name = Column(String(100), nullable=False)

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    phone = Column(String(10), nullable=False)

    department_id = Column(
        Integer,
        ForeignKey("departments.department_id"),
        nullable=False
    )

    designation = Column(String(100), nullable=False)

    salary = Column(Float, nullable=False)

    date_of_joining = Column(Date, nullable=False)

    employment_type = Column(
        String(20),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
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

    department = relationship(
        "Department",
        back_populates="employees"
    )

    leave_requests = relationship(
        "LeaveRequest",
        back_populates="employee"
    )