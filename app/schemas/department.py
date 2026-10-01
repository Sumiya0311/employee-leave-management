from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
class DepartmentBase(BaseModel):
    department_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )
    location: str = Field(
        ...,
        min_length=2,
        max_length=100
    )
    is_active: bool = True

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    department_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(
        from_attributes=True
    )