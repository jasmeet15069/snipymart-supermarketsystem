from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    CASHIER = "CASHIER"


class PaymentMode(str, enum.Enum):
    CASH = "CASH"
    UPI = "UPI"
    CARD = "CARD"


class ShiftStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class SaleStatus(str, enum.Enum):
    COMPLETED = "COMPLETED"
    PARTIALLY_RETURNED = "PARTIALLY_RETURNED"
    RETURNED = "RETURNED"
    VOID = "VOID"


class StockMovementType(str, enum.Enum):
    PURCHASE_IN = "PURCHASE_IN"
    SALE_OUT = "SALE_OUT"
    RETURN_IN = "RETURN_IN"
    ADJUSTMENT_IN = "ADJUSTMENT_IN"
    ADJUSTMENT_OUT = "ADJUSTMENT_OUT"


class PurchaseOrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ORDERED = "ORDERED"
    PARTIAL = "PARTIAL"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum=False, length=20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sales: Mapped[list[Sale]] = relationship(back_populates="cashier")
    shifts: Mapped[list[CashierShift]] = relationship(back_populates="cashier")


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    default_gst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    products: Mapped[list[Product]] = relationship(back_populates="category")


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("selling_price >= 0", name="ck_products_selling_price_non_negative"),
        CheckConstraint("cost_price >= 0", name="ck_products_cost_price_non_negative"),
        CheckConstraint("gst_rate >= 0", name="ck_products_gst_rate_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    sku: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(80), unique=True, index=True)
    brand: Mapped[str | None] = mapped_column(String(80))
    hsn_code: Mapped[str | None] = mapped_column(String(20))
    shelf_location: Mapped[str | None] = mapped_column(String(60))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    min_margin_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("12.00"), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="pcs", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category: Mapped[Category | None] = relationship(back_populates="products")
    inventory: Mapped[InventoryItem | None] = relationship(back_populates="product", uselist=False, cascade="all, delete-orphan")
    batches: Mapped[list[InventoryBatch]] = relationship(back_populates="product")
    sale_items: Mapped[list[SaleItem]] = relationship(back_populates="product")


class InventoryItem(TimestampMixin, Base):
    __tablename__ = "inventory_items"
    __table_args__ = (
        CheckConstraint("on_hand >= 0", name="ck_inventory_on_hand_non_negative"),
        CheckConstraint("reorder_level >= 0", name="ck_inventory_reorder_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False)
    on_hand: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"), nullable=False)
    reorder_level: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("5.000"), nullable=False)
    safety_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"), nullable=False)

    product: Mapped[Product] = relationship(back_populates="inventory")


class InventoryBatch(TimestampMixin, Base):
    __tablename__ = "inventory_batches"
    __table_args__ = (
        UniqueConstraint("product_id", "batch_number", name="uq_inventory_batches_product_batch"),
        CheckConstraint("quantity_on_hand >= 0", name="ck_batches_qty_non_negative"),
        CheckConstraint("received_quantity >= 0", name="ck_batches_received_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    batch_number: Mapped[str] = mapped_column(String(120), nullable=False)
    supplier_batch_code: Mapped[str | None] = mapped_column(String(120))
    expiry_date: Mapped[date | None] = mapped_column(Date)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    mrp: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    received_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    quantity_on_hand: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)

    product: Mapped[Product] = relationship(back_populates="batches")
    movements: Mapped[list[StockMovement]] = relationship(back_populates="batch")


class StockMovement(TimestampMixin, Base):
    __tablename__ = "stock_movements"
    __table_args__ = (Index("ix_stock_movements_product_created", "product_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("inventory_batches.id", ondelete="SET NULL"), index=True)
    movement_type: Mapped[StockMovementType] = mapped_column(Enum(StockMovementType, native_enum=False, length=30), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    before_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    after_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(50))
    reference_id: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(String(255))
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    product: Mapped[Product] = relationship()
    batch: Mapped[InventoryBatch | None] = relationship(back_populates="movements")
    created_by: Mapped[User | None] = relationship()


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(40), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(Text)
    loyalty_tier: Mapped[str] = mapped_column(String(30), default="REGULAR", nullable=False)
    loyalty_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sales: Mapped[list[Sale]] = relationship(back_populates="customer")
    loyalty_ledger: Mapped[list[LoyaltyLedger]] = relationship(back_populates="customer")


class CashierShift(TimestampMixin, Base):
    __tablename__ = "cashier_shifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cashier_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[ShiftStatus] = mapped_column(Enum(ShiftStatus, native_enum=False, length=20), default=ShiftStatus.OPEN, nullable=False)
    opened_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)
    opening_cash: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    closing_cash: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    expected_cash: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    variance: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    cashier: Mapped[User] = relationship(back_populates="shifts")
    sales: Mapped[list[Sale]] = relationship(back_populates="shift")


class Sale(TimestampMixin, Base):
    __tablename__ = "sales"
    __table_args__ = (Index("ix_sales_created_cashier", "created_at", "cashier_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_number: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    cashier_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"))
    shift_id: Mapped[int | None] = mapped_column(ForeignKey("cashier_shifts.id", ondelete="SET NULL"))
    status: Mapped[SaleStatus] = mapped_column(Enum(SaleStatus, native_enum=False, length=30), default=SaleStatus.COMPLETED, nullable=False)
    channel: Mapped[str] = mapped_column(String(30), default="POS", nullable=False)
    payment_status: Mapped[str] = mapped_column(String(30), default="PAID", nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    taxable_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tax_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    grand_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    paid_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    change_due: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255))

    cashier: Mapped[User] = relationship(back_populates="sales")
    customer: Mapped[Customer | None] = relationship(back_populates="sales")
    shift: Mapped[CashierShift | None] = relationship(back_populates="sales")
    items: Mapped[list[SaleItem]] = relationship(back_populates="sale", cascade="all, delete-orphan")
    payments: Mapped[list[Payment]] = relationship(back_populates="sale", cascade="all, delete-orphan")
    returns: Mapped[list[SaleReturn]] = relationship(back_populates="sale")


class SaleItem(TimestampMixin, Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(180), nullable=False)
    sku: Mapped[str] = mapped_column(String(80), nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(80))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    returned_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    gst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    taxable_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    sale: Mapped[Sale] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="sale_items")
    allocations: Mapped[list[SaleItemBatchAllocation]] = relationship(back_populates="sale_item", cascade="all, delete-orphan")


class SaleItemBatchAllocation(TimestampMixin, Base):
    __tablename__ = "sale_item_batch_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_item_id: Mapped[int] = mapped_column(ForeignKey("sale_items.id", ondelete="CASCADE"), index=True, nullable=False)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("inventory_batches.id", ondelete="SET NULL"), index=True)
    batch_number: Mapped[str] = mapped_column(String(120), nullable=False)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    returned_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"), nullable=False)

    sale_item: Mapped[SaleItem] = relationship(back_populates="allocations")
    batch: Mapped[InventoryBatch | None] = relationship()


class Payment(TimestampMixin, Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"), index=True, nullable=False)
    mode: Mapped[PaymentMode] = mapped_column(Enum(PaymentMode, native_enum=False, length=20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(120))

    sale: Mapped[Sale] = relationship(back_populates="payments")


class SaleReturn(TimestampMixin, Base):
    __tablename__ = "sale_returns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="RESTRICT"), nullable=False)
    refund_mode: Mapped[PaymentMode] = mapped_column(Enum(PaymentMode, native_enum=False, length=20), nullable=False)
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255))
    processed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    sale: Mapped[Sale] = relationship(back_populates="returns")
    processed_by: Mapped[User | None] = relationship()
    items: Mapped[list[SaleReturnItem]] = relationship(back_populates="sale_return", cascade="all, delete-orphan")


class SaleReturnItem(TimestampMixin, Base):
    __tablename__ = "sale_return_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_return_id: Mapped[int] = mapped_column(ForeignKey("sale_returns.id", ondelete="CASCADE"), nullable=False)
    sale_item_id: Mapped[int] = mapped_column(ForeignKey("sale_items.id", ondelete="RESTRICT"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    sale_return: Mapped[SaleReturn] = relationship(back_populates="items")
    sale_item: Mapped[SaleItem] = relationship()
    product: Mapped[Product] = relationship()


class Supplier(TimestampMixin, Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(40))
    email: Mapped[str | None] = mapped_column(String(255))
    gstin: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(Text)
    payment_terms: Mapped[str | None] = mapped_column(String(80))
    credit_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    purchase_orders: Mapped[list[PurchaseOrder]] = relationship(back_populates="supplier")


class PurchaseOrder(TimestampMixin, Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    po_number: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[PurchaseOrderStatus] = mapped_column(
        Enum(PurchaseOrderStatus, native_enum=False, length=20),
        default=PurchaseOrderStatus.ORDERED,
        nullable=False,
    )
    expected_date: Mapped[date | None] = mapped_column(Date)
    payment_status: Mapped[str] = mapped_column(String(30), default="UNPAID", nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tax_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    grand_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255))
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    supplier: Mapped[Supplier] = relationship(back_populates="purchase_orders")
    created_by: Mapped[User | None] = relationship()
    items: Mapped[list[PurchaseOrderItem]] = relationship(back_populates="purchase_order", cascade="all, delete-orphan")
    receipts: Mapped[list[GoodsReceipt]] = relationship(back_populates="purchase_order")


class PurchaseOrderItem(TimestampMixin, Base):
    __tablename__ = "purchase_order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchase_order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity_ordered: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    quantity_received: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    purchase_order: Mapped[PurchaseOrder] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()


class GoodsReceipt(TimestampMixin, Base):
    __tablename__ = "goods_receipts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grn_number: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    purchase_order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id", ondelete="RESTRICT"), nullable=False)
    supplier_invoice_number: Mapped[str | None] = mapped_column(String(120))
    received_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    received_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    notes: Mapped[str | None] = mapped_column(String(255))

    purchase_order: Mapped[PurchaseOrder] = relationship(back_populates="receipts")
    received_by: Mapped[User | None] = relationship()
    items: Mapped[list[GoodsReceiptItem]] = relationship(back_populates="goods_receipt", cascade="all, delete-orphan")


class GoodsReceiptItem(TimestampMixin, Base):
    __tablename__ = "goods_receipt_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goods_receipt_id: Mapped[int] = mapped_column(ForeignKey("goods_receipts.id", ondelete="CASCADE"), nullable=False)
    purchase_order_item_id: Mapped[int] = mapped_column(ForeignKey("purchase_order_items.id", ondelete="RESTRICT"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("inventory_batches.id", ondelete="SET NULL"))
    batch_number: Mapped[str] = mapped_column(String(120), nullable=False)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    quantity_received: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    goods_receipt: Mapped[GoodsReceipt] = relationship(back_populates="items")
    purchase_order_item: Mapped[PurchaseOrderItem] = relationship()
    product: Mapped[Product] = relationship()
    batch: Mapped[InventoryBatch | None] = relationship()


class LoyaltyLedger(TimestampMixin, Base):
    __tablename__ = "loyalty_ledger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    sale_id: Mapped[int | None] = mapped_column(ForeignKey("sales.id", ondelete="SET NULL"))
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(160), nullable=False)

    customer: Mapped[Customer] = relationship(back_populates="loyalty_ledger")
    sale: Mapped[Sale | None] = relationship()
