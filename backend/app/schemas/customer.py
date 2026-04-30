from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class CustomerBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    address: str | None = None
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    address: str | None = None
    is_active: bool | None = None


class CustomerRead(CustomerBase, ORMModel):
    id: int
    loyalty_points: int
    created_at: datetime
    updated_at: datetime
