from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.domain import (
    Category,
    Customer,
    InventoryBatch,
    InventoryItem,
    Product,
    StockMovement,
    StockMovementType,
    Supplier,
    User,
    UserRole,
)


def get_or_create_user(db, email: str, full_name: str, password: str, role: UserRole) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user:
        return user
    user = User(email=email, full_name=full_name, hashed_password=hash_password(password), role=role, is_active=True)
    db.add(user)
    db.flush()
    return user


def get_or_create_category(db, name: str, gst_rate: str) -> Category:
    category = db.scalar(select(Category).where(Category.name == name))
    if category:
        return category
    category = Category(name=name, default_gst_rate=Decimal(gst_rate), is_active=True)
    db.add(category)
    db.flush()
    return category


def get_or_create_supplier(db, name: str, phone: str) -> Supplier:
    supplier = db.scalar(select(Supplier).where(Supplier.name == name))
    if supplier:
        return supplier
    supplier = Supplier(name=name, contact_name="Procurement Desk", phone=phone, email=None, is_active=True)
    db.add(supplier)
    db.flush()
    return supplier


def seed_product(
    db,
    admin: User,
    category: Category,
    name: str,
    sku: str,
    barcode: str,
    selling_price: str,
    cost_price: str,
    gst_rate: str,
    quantity: str,
    reorder_level: str,
    batch_number: str,
    expires_in_days: int | None,
) -> None:
    if db.scalar(select(Product).where(Product.sku == sku)):
        return
    product = Product(
        name=name,
        sku=sku,
        barcode=barcode,
        category_id=category.id,
        selling_price=Decimal(selling_price),
        cost_price=Decimal(cost_price),
        gst_rate=Decimal(gst_rate),
        unit="pcs",
        is_active=True,
    )
    db.add(product)
    db.flush()
    inventory = InventoryItem(product_id=product.id, on_hand=Decimal(quantity), reorder_level=Decimal(reorder_level))
    db.add(inventory)
    batch = InventoryBatch(
        product_id=product.id,
        batch_number=batch_number,
        expiry_date=date.today() + timedelta(days=expires_in_days) if expires_in_days else None,
        cost_price=Decimal(cost_price),
        received_quantity=Decimal(quantity),
        quantity_on_hand=Decimal(quantity),
    )
    db.add(batch)
    db.flush()
    db.add(
        StockMovement(
            product_id=product.id,
            batch_id=batch.id,
            movement_type=StockMovementType.ADJUSTMENT_IN,
            quantity=Decimal(quantity),
            before_quantity=Decimal("0.000"),
            after_quantity=Decimal(quantity),
            reference_type="SEED",
            notes="Seed opening stock",
            created_by_id=admin.id,
        )
    )


def main() -> None:
    db = SessionLocal()
    try:
        admin = get_or_create_user(db, settings.first_superuser_email, "Store Admin", settings.first_superuser_password, UserRole.ADMIN)
        get_or_create_user(db, settings.first_cashier_email, "POS Cashier", settings.first_cashier_password, UserRole.CASHIER)

        staples = get_or_create_category(db, "Staples", "5.00")
        dairy = get_or_create_category(db, "Dairy", "5.00")
        snacks = get_or_create_category(db, "Snacks", "12.00")
        household = get_or_create_category(db, "Household", "18.00")

        get_or_create_supplier(db, "FreshLine Distributors", "+91-9876543210")
        get_or_create_supplier(db, "Daily Needs Wholesale", "+91-9123456780")

        if not db.scalar(select(Customer).where(Customer.phone == "+91-9000000001")):
            db.add(Customer(name="Walk-in Loyalty Customer", phone="+91-9000000001", email="loyalty@example.com", loyalty_points=0))

        seed_product(db, admin, staples, "India Gate Basmati Rice 5kg", "ST-RICE-5KG", "8901001000011", "649.00", "560.00", "5.00", "40.000", "8.000", "RICE-APR26", 365)
        seed_product(db, admin, dairy, "Amul Taaza Milk 1L", "DA-MILK-1L", "8901262010010", "68.00", "58.00", "5.00", "80.000", "20.000", "MILK-APR30", 4)
        seed_product(db, admin, snacks, "Lay's Classic Salted 52g", "SN-LAYS-52", "8901491100110", "20.00", "15.00", "12.00", "120.000", "30.000", "LAYS-MAR26", 180)
        seed_product(db, admin, household, "Surf Excel Detergent 1kg", "HH-SURF-1KG", "8901030821122", "245.00", "210.00", "18.00", "30.000", "8.000", "SURF-FEB26", 720)
        seed_product(db, admin, staples, "Tata Salt 1kg", "ST-SALT-1KG", "8904043901012", "28.00", "22.00", "5.00", "100.000", "25.000", "SALT-JAN26", 540)

        db.commit()
        print("Seed data loaded. Admin: admin@snipymart.in / Admin@12345; Cashier: cashier@snipymart.in / Cashier@12345")
    finally:
        db.close()


if __name__ == "__main__":
    main()
