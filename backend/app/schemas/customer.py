from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class CustomerBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    address: str | None = None
    loyalty_tier: str = Field(default="REGULAR", max_length=30)
    credit_limit: Decimal = Field(default=Decimal("0.00"), ge=0)
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    address: str | None = None
    loyalty_tier: str | None = Field(default=None, max_length=30)
    credit_limit: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None


class CustomerRead(CustomerBase, ORMModel):
    id: int
    loyalty_points: int
    created_at: datetime
    updated_at: datetime
