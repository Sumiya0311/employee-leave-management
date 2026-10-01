from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
class Department(Base):
    __tablename__ = "departments"
    department_id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String(100), unique=True, nullable=False)
    location = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    employees = relationship("Employee", back_populates="department")