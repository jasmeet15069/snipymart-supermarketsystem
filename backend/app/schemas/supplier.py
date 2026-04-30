from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class SupplierBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    contact_name: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    gstin: str | None = Field(default=None, max_length=30)
    address: str | None = None
    payment_terms: str | None = Field(default=None, max_length=80)
    credit_days: int = Field(default=0, ge=0, le=180)
    is_active: bool = True


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    contact_name: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    gstin: str | None = Field(default=None, max_length=30)
    address: str | None = None
    payment_terms: str | None = Field(default=None, max_length=80)
    credit_days: int | None = Field(default=None, ge=0, le=180)
    is_active: bool | None = None


class SupplierRead(SupplierBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime
