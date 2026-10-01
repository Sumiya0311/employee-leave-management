from pydantic import BaseModel, ConfigDict, EmailStr, Field
class RegisterRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=100
    )

    role: str = "Employee"

    employee_id: int | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    employee_id: int | None
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )