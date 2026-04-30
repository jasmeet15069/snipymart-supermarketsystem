from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.errors import BusinessError
from app.models.domain import Base, CashierShift, Category, InventoryBatch, InventoryItem, Product, ShiftStatus, User, UserRole
from app.schemas.sales import PaymentCreate, SaleCreate, SaleItemCreate
from app.models.domain import PaymentMode
from app.services.sales import create_sale


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def seed_sale_data(db):
    user = User(email="cashier@example.com", full_name="Cashier", hashed_password="x", role=UserRole.CASHIER)
    category = Category(name="Staples", default_gst_rate=Decimal("5.00"))
    db.add_all([user, category])
    db.flush()
    shift = CashierShift(cashier_id=user.id, status=ShiftStatus.OPEN, opening_cash=Decimal("100.00"))
    product = Product(
        name="Rice 1kg",
        sku="RICE-1",
        barcode="1001",
        category_id=category.id,
        selling_price=Decimal("105.00"),
        cost_price=Decimal("80.00"),
        gst_rate=Decimal("5.00"),
        unit="pcs",
    )
    db.add_all([shift, product])
    db.flush()
    db.add(InventoryItem(product_id=product.id, on_hand=Decimal("10.000"), reorder_level=Decimal("2.000")))
    db.add(
        InventoryBatch(
            product_id=product.id,
            batch_number="B1",
            cost_price=Decimal("80.00"),
            received_quantity=Decimal("10.000"),
            quantity_on_hand=Decimal("10.000"),
        )
    )
    db.commit()
    return user, product


def test_sale_deducts_fifo_stock_and_records_totals(db):
    user, product = seed_sale_data(db)
    sale = create_sale(
        db,
        SaleCreate(
            items=[SaleItemCreate(product_id=product.id, quantity=Decimal("2.000"))],
            payments=[PaymentCreate(mode=PaymentMode.CASH, amount=Decimal("210.00"))],
        ),
        user,
    )

    inventory = db.scalar(select(InventoryItem).where(InventoryItem.product_id == product.id))
    batch = db.scalar(select(InventoryBatch).where(InventoryBatch.product_id == product.id))
    assert sale.grand_total == Decimal("210.00")
    assert sale.tax_total == Decimal("10.00")
    assert inventory.on_hand == Decimal("8.000")
    assert batch.quantity_on_hand == Decimal("8.000")


def test_sale_blocks_negative_stock(db):
    user, product = seed_sale_data(db)
    with pytest.raises(BusinessError):
        create_sale(
            db,
            SaleCreate(
                items=[SaleItemCreate(product_id=product.id, quantity=Decimal("11.000"))],
                payments=[PaymentCreate(mode=PaymentMode.CASH, amount=Decimal("1200.00"))],
            ),
            user,
        )
    inventory = db.scalar(select(InventoryItem).where(InventoryItem.product_id == product.id))
    assert inventory.on_hand == Decimal("10.000")
