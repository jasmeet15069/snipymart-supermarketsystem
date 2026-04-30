from pydantic import BaseModel, EmailStr, Field

from app.models.domain import UserRole
from app.schemas.common import ORMModel


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserRead(ORMModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8)
    role: UserRole
    is_active: bool = True


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    password: str | None = Field(default=None, min_length=8)
    role: UserRole | None = None
    is_active: bool | None = None
