from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CategoryBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    default_gst_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=40)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    default_gst_rate: Decimal | None = Field(default=None, ge=0, le=40)
    is_active: bool | None = None


class CategoryRead(CategoryBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime


class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    sku: str = Field(min_length=2, max_length=80)
    barcode: str | None = Field(default=None, max_length=80)
    category_id: int | None = None
    selling_price: Decimal = Field(ge=0)
    cost_price: Decimal = Field(ge=0)
    gst_rate: Decimal = Field(ge=0, le=40)
    unit: str = Field(default="pcs", max_length=20)
    reorder_level: Decimal = Field(default=Decimal("5.000"), ge=0)
    is_active: bool = True


class ProductCreate(ProductBase):
    opening_quantity: Decimal = Field(default=Decimal("0.000"), ge=0)
    opening_batch_number: str | None = Field(default=None, max_length=120)
    opening_expiry_date: date | None = None


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    sku: str | None = Field(default=None, min_length=2, max_length=80)
    barcode: str | None = Field(default=None, max_length=80)
    category_id: int | None = None
    selling_price: Decimal | None = Field(default=None, ge=0)
    cost_price: Decimal | None = Field(default=None, ge=0)
    gst_rate: Decimal | None = Field(default=None, ge=0, le=40)
    unit: str | None = Field(default=None, max_length=20)
    reorder_level: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductRead(ORMModel):
    id: int
    name: str
    sku: str
    barcode: str | None
    category_id: int | None
    selling_price: Decimal
    cost_price: Decimal
    gst_rate: Decimal
    unit: str
    is_active: bool
    on_hand: Decimal = Decimal("0.000")
    reorder_level: Decimal = Decimal("0.000")
    category_name: str | None = None
    created_at: datetime
    updated_at: datetime


class InventoryBatchRead(ORMModel):
    id: int
    product_id: int
    batch_number: str
    expiry_date: date | None
    cost_price: Decimal
    received_quantity: Decimal
    quantity_on_hand: Decimal
    created_at: datetime


class InventoryRow(ORMModel):
    product_id: int
    product_name: str
    sku: str
    barcode: str | None
    on_hand: Decimal
    reorder_level: Decimal
    is_low_stock: bool
    batches: list[InventoryBatchRead] = []


class StockMovementRead(ORMModel):
    id: int
    product_id: int
    product_name: str | None = None
    batch_id: int | None
    movement_type: str
    quantity: Decimal
    before_quantity: Decimal
    after_quantity: Decimal
    reference_type: str | None
    reference_id: int | None
    notes: str | None
    created_at: datetime
