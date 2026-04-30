from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.domain import PurchaseOrderStatus
from app.schemas.common import ORMModel


class PurchaseOrderItemCreate(BaseModel):
    product_id: int
    quantity_ordered: Decimal = Field(gt=0)
    unit_cost: Decimal = Field(ge=0)
    gst_rate: Decimal = Field(ge=0, le=40)


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    expected_date: date | None = None
    notes: str | None = Field(default=None, max_length=255)
    items: list[PurchaseOrderItemCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def ensure_unique_products(self) -> "PurchaseOrderCreate":
        product_ids = [item.product_id for item in self.items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Each product can appear only once per purchase order")
        return self


class PurchaseOrderItemRead(ORMModel):
    id: int
    product_id: int
    quantity_ordered: Decimal
    quantity_received: Decimal
    unit_cost: Decimal
    gst_rate: Decimal
    line_total: Decimal


class PurchaseOrderRead(ORMModel):
    id: int
    po_number: str
    supplier_id: int
    status: PurchaseOrderStatus
    payment_status: str
    expected_date: date | None
    subtotal: Decimal
    tax_total: Decimal
    grand_total: Decimal
    notes: str | None
    created_at: datetime
    items: list[PurchaseOrderItemRead] = []


class PurchaseOrderListRow(ORMModel):
    id: int
    po_number: str
    supplier_name: str
    status: PurchaseOrderStatus
    payment_status: str
    grand_total: Decimal
    expected_date: date | None
    created_at: datetime


class GoodsReceiptItemCreate(BaseModel):
    purchase_order_item_id: int
    batch_number: str = Field(min_length=1, max_length=120)
    expiry_date: date | None = None
    quantity_received: Decimal = Field(gt=0)
    unit_cost: Decimal = Field(ge=0)


class GoodsReceiptCreate(BaseModel):
    supplier_invoice_number: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=255)
    items: list[GoodsReceiptItemCreate] = Field(min_length=1)


class GoodsReceiptItemRead(ORMModel):
    id: int
    purchase_order_item_id: int
    product_id: int
    batch_id: int | None
    batch_number: str
    expiry_date: date | None
    quantity_received: Decimal
    unit_cost: Decimal


class GoodsReceiptRead(ORMModel):
    id: int
    grn_number: str
    purchase_order_id: int
    supplier_invoice_number: str | None
    received_at: datetime
    notes: str | None
    items: list[GoodsReceiptItemRead] = []
