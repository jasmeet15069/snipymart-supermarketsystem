from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.domain import PaymentMode, SaleStatus
from app.schemas.common import ORMModel


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: Decimal = Field(gt=0)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)


class PaymentCreate(BaseModel):
    mode: PaymentMode
    amount: Decimal = Field(gt=0)
    reference: str | None = Field(default=None, max_length=120)


class SaleCreate(BaseModel):
    customer_id: int | None = None
    items: list[SaleItemCreate] = Field(min_length=1)
    payments: list[PaymentCreate] = Field(min_length=1)
    notes: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def ensure_unique_products(self) -> "SaleCreate":
        product_ids = [item.product_id for item in self.items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Each product can appear only once per sale")
        return self


class PaymentRead(ORMModel):
    id: int
    mode: PaymentMode
    amount: Decimal
    reference: str | None


class SaleItemAllocationRead(ORMModel):
    id: int
    batch_id: int | None
    batch_number: str
    expiry_date: date | None
    quantity: Decimal
    returned_quantity: Decimal


class SaleItemRead(ORMModel):
    id: int
    product_id: int
    product_name: str
    sku: str
    barcode: str | None
    quantity: Decimal
    returned_quantity: Decimal
    unit_price: Decimal
    discount_amount: Decimal
    gst_rate: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal
    line_total: Decimal
    allocations: list[SaleItemAllocationRead] = []


class SaleRead(ORMModel):
    id: int
    invoice_number: str
    cashier_id: int
    customer_id: int | None
    shift_id: int | None
    status: SaleStatus
    subtotal: Decimal
    discount_total: Decimal
    taxable_total: Decimal
    tax_total: Decimal
    grand_total: Decimal
    paid_total: Decimal
    change_due: Decimal
    notes: str | None
    created_at: datetime
    items: list[SaleItemRead] = []
    payments: list[PaymentRead] = []


class SaleListRow(ORMModel):
    id: int
    invoice_number: str
    status: SaleStatus
    cashier_name: str
    customer_name: str | None
    grand_total: Decimal
    paid_total: Decimal
    created_at: datetime


class ReturnItemCreate(BaseModel):
    sale_item_id: int
    quantity: Decimal = Field(gt=0)


class SaleReturnCreate(BaseModel):
    refund_mode: PaymentMode
    reason: str | None = Field(default=None, max_length=255)
    items: list[ReturnItemCreate] = Field(min_length=1)


class SaleReturnItemRead(ORMModel):
    id: int
    sale_item_id: int
    product_id: int
    quantity: Decimal
    refund_amount: Decimal


class SaleReturnRead(ORMModel):
    id: int
    sale_id: int
    refund_mode: PaymentMode
    refund_amount: Decimal
    reason: str | None
    created_at: datetime
    items: list[SaleReturnItemRead] = []
