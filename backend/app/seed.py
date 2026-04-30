from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.domain import (
    CashierShift,
    Category,
    Customer,
    GoodsReceipt,
    InventoryBatch,
    InventoryItem,
    PaymentMode,
    Product,
    PurchaseOrder,
    Sale,
    SaleReturn,
    ShiftStatus,
    StockMovement,
    StockMovementType,
    Supplier,
    User,
    UserRole,
)
from app.schemas.purchases import GoodsReceiptCreate, GoodsReceiptItemCreate, PurchaseOrderCreate, PurchaseOrderItemCreate
from app.schemas.sales import PaymentCreate, ReturnItemCreate, SaleCreate, SaleItemCreate, SaleReturnCreate
from app.services.decimal_utils import money, qty
from app.services.purchases import create_purchase_order, receive_goods
from app.services.sales import create_return, create_sale, loyalty_tier_for


def get_or_create_user(db, email: str, full_name: str, password: str, role: UserRole) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user:
        user.full_name = full_name
        user.role = role
        user.is_active = True
        return user
    user = User(email=email, full_name=full_name, hashed_password=hash_password(password), role=role, is_active=True)
    db.add(user)
    db.flush()
    return user


def get_or_create_category(db, name: str, gst_rate: str, description: str) -> Category:
    category = db.scalar(select(Category).where(Category.name == name))
    if not category:
        category = Category(name=name, default_gst_rate=Decimal(gst_rate), description=description, is_active=True)
        db.add(category)
        db.flush()
    else:
        category.default_gst_rate = Decimal(gst_rate)
        category.description = description
        category.is_active = True
    return category


def get_or_create_supplier(
    db,
    name: str,
    contact_name: str,
    phone: str,
    email: str,
    gstin: str,
    address: str,
    payment_terms: str,
    credit_days: int,
) -> Supplier:
    supplier = db.scalar(select(Supplier).where(Supplier.name == name))
    if not supplier:
        supplier = Supplier(name=name)
        db.add(supplier)
        db.flush()
    supplier.contact_name = contact_name
    supplier.phone = phone
    supplier.email = email
    supplier.gstin = gstin
    supplier.address = address
    supplier.payment_terms = payment_terms
    supplier.credit_days = credit_days
    supplier.is_active = True
    return supplier


def get_or_create_customer(
    db,
    name: str,
    phone: str,
    email: str,
    address: str,
    loyalty_points: int,
    credit_limit: str,
) -> Customer:
    customer = db.scalar(select(Customer).where(Customer.phone == phone))
    if not customer:
        customer = Customer(name=name, phone=phone)
        db.add(customer)
        db.flush()
    customer.name = name
    customer.email = email
    customer.address = address
    customer.loyalty_points = max(customer.loyalty_points or 0, loyalty_points)
    customer.loyalty_tier = loyalty_tier_for(customer.loyalty_points)
    customer.credit_limit = Decimal(credit_limit)
    customer.is_active = True
    return customer


def seed_product(db, admin: User, category: Category, data: dict) -> Product:
    product = db.scalar(select(Product).where(Product.sku == data["sku"]))
    created = product is None
    if not product:
        product = Product(sku=data["sku"])
        db.add(product)

    product.name = data["name"]
    product.barcode = data["barcode"]
    product.brand = data["brand"]
    product.hsn_code = data["hsn_code"]
    product.shelf_location = data["shelf_location"]
    product.category_id = category.id
    product.selling_price = Decimal(data["selling_price"])
    product.cost_price = Decimal(data["cost_price"])
    product.gst_rate = Decimal(data["gst_rate"])
    product.min_margin_percent = Decimal(data["min_margin_percent"])
    product.unit = data["unit"]
    product.is_active = True
    db.flush()

    inventory = product.inventory or db.scalar(select(InventoryItem).where(InventoryItem.product_id == product.id))
    if not inventory:
        inventory = InventoryItem(product_id=product.id, on_hand=Decimal("0.000"))
        db.add(inventory)
        db.flush()
    inventory.reorder_level = Decimal(data["reorder_level"])
    inventory.safety_stock = Decimal(data["safety_stock"])

    if created and Decimal(data["opening_quantity"]) > 0:
        opening_qty = Decimal(data["opening_quantity"])
        inventory.on_hand = opening_qty
        batch = InventoryBatch(
            product_id=product.id,
            batch_number=data["batch_number"],
            supplier_batch_code=data.get("supplier_batch_code"),
            expiry_date=date.today() + timedelta(days=data["expires_in_days"]) if data.get("expires_in_days") else None,
            cost_price=Decimal(data["cost_price"]),
            mrp=Decimal(data["selling_price"]),
            received_quantity=opening_qty,
            quantity_on_hand=opening_qty,
        )
        db.add(batch)
        db.flush()
        db.add(
            StockMovement(
                product_id=product.id,
                batch_id=batch.id,
                movement_type=StockMovementType.ADJUSTMENT_IN,
                quantity=opening_qty,
                before_quantity=Decimal("0.000"),
                after_quantity=opening_qty,
                reference_type="SEED_OPENING",
                notes="Business demo opening stock",
                created_by_id=admin.id,
            )
        )
    return product


def ensure_open_shift(db, cashier: User) -> CashierShift:
    shift = db.scalar(select(CashierShift).where(CashierShift.cashier_id == cashier.id, CashierShift.status == ShiftStatus.OPEN))
    if shift:
        return shift
    shift = CashierShift(cashier_id=cashier.id, status=ShiftStatus.OPEN, opening_cash=Decimal("5000.00"))
    db.add(shift)
    db.flush()
    return shift


def products_by_sku(db) -> dict[str, Product]:
    return {product.sku: product for product in db.scalars(select(Product))}


def sale_total(product_map: dict[str, Product], lines: list[dict]) -> Decimal:
    total = Decimal("0.00")
    for line in lines:
        product = product_map[line["sku"]]
        total += money(product.selling_price * Decimal(line["qty"]) - Decimal(line.get("discount", "0.00")))
    return money(total)


def create_demo_sale(db, cashier: User, product_map: dict[str, Product], data: dict) -> Sale:
    existing = db.scalar(select(Sale).where(Sale.notes == data["notes"]))
    if existing:
        return existing
    total = sale_total(product_map, data["lines"])
    payment_amount = Decimal(data.get("paid", total))
    sale = create_sale(
        db,
        SaleCreate(
            customer_id=data.get("customer_id"),
            notes=data["notes"],
            items=[
                SaleItemCreate(product_id=product_map[line["sku"]].id, quantity=Decimal(line["qty"]), discount_amount=Decimal(line.get("discount", "0.00")))
                for line in data["lines"]
            ],
            payments=[PaymentCreate(mode=data["mode"], amount=payment_amount, reference=data.get("reference"))],
        ),
        cashier,
    )
    created_at = datetime.combine(date.today() - timedelta(days=data["days_ago"]), time(hour=data["hour"], minute=data["minute"]))
    persisted = db.get(Sale, sale.id)
    persisted.created_at = created_at
    persisted.updated_at = created_at
    for item in persisted.items:
        item.created_at = created_at
        item.updated_at = created_at
    for payment in persisted.payments:
        payment.created_at = created_at
        payment.updated_at = created_at
    db.commit()
    db.refresh(persisted)
    return persisted


def create_demo_purchase_order(db, admin: User, supplier: Supplier, product_map: dict[str, Product], data: dict) -> PurchaseOrder:
    existing = db.scalar(select(PurchaseOrder).where(PurchaseOrder.notes == data["notes"]))
    if existing:
        return existing
    po = create_purchase_order(
        db,
        PurchaseOrderCreate(
            supplier_id=supplier.id,
            expected_date=date.today() + timedelta(days=data.get("expected_in_days", 2)),
            notes=data["notes"],
            items=[
                PurchaseOrderItemCreate(
                    product_id=product_map[item["sku"]].id,
                    quantity_ordered=Decimal(item["qty"]),
                    unit_cost=Decimal(item["unit_cost"]),
                    gst_rate=Decimal(item["gst_rate"]),
                )
                for item in data["items"]
            ],
        ),
        admin,
    )
    persisted = db.scalar(select(PurchaseOrder).where(PurchaseOrder.id == po.id).options(selectinload(PurchaseOrder.items)))
    created_at = datetime.combine(date.today() - timedelta(days=data.get("days_ago", 1)), time(hour=10, minute=15))
    persisted.created_at = created_at
    persisted.updated_at = created_at
    persisted.payment_status = data.get("payment_status", "UNPAID")
    db.commit()
    db.refresh(persisted)
    return persisted


def receive_demo_goods(db, admin: User, po: PurchaseOrder, data: dict) -> GoodsReceipt | None:
    if db.scalar(select(GoodsReceipt).where(GoodsReceipt.notes == data["notes"])):
        return None
    po = db.scalar(select(PurchaseOrder).where(PurchaseOrder.id == po.id).options(selectinload(PurchaseOrder.items)))
    items_by_sku = {db.get(Product, item.product_id).sku: item for item in po.items}
    receipt = receive_goods(
        db,
        po.id,
        GoodsReceiptCreate(
            supplier_invoice_number=data.get("supplier_invoice_number"),
            notes=data["notes"],
            items=[
                GoodsReceiptItemCreate(
                    purchase_order_item_id=items_by_sku[item["sku"]].id,
                    batch_number=item["batch_number"],
                    expiry_date=date.today() + timedelta(days=item["expires_in_days"]) if item.get("expires_in_days") else None,
                    quantity_received=Decimal(item["qty"]),
                    unit_cost=Decimal(item["unit_cost"]),
                )
                for item in data["items"]
            ],
        ),
        admin,
    )
    received_at = datetime.combine(date.today() - timedelta(days=data.get("days_ago", 0)), time(hour=16, minute=20))
    persisted = db.get(GoodsReceipt, receipt.id)
    persisted.received_at = received_at
    persisted.created_at = received_at
    persisted.updated_at = received_at
    if data.get("po_payment_status"):
        po = db.get(PurchaseOrder, po.id)
        po.payment_status = data["po_payment_status"]
    db.commit()
    db.refresh(persisted)
    return persisted


def main() -> None:
    db = SessionLocal()
    try:
        admin = get_or_create_user(db, settings.first_superuser_email, "Store Admin", settings.first_superuser_password, UserRole.ADMIN)
        cashier = get_or_create_user(db, settings.first_cashier_email, "POS Cashier", settings.first_cashier_password, UserRole.CASHIER)
        get_or_create_user(db, "manager@snipymart.in", "Store Manager", "Manager@12345", UserRole.ADMIN)

        categories = {
            "Staples": get_or_create_category(db, "Staples", "5.00", "Rice, atta, salt, oil and pantry essentials"),
            "Dairy": get_or_create_category(db, "Dairy", "0.00", "Milk, butter, curd and chilled products"),
            "Snacks": get_or_create_category(db, "Snacks", "12.00", "Biscuits, chips and namkeen"),
            "Household": get_or_create_category(db, "Household", "18.00", "Cleaning and home care products"),
            "Personal Care": get_or_create_category(db, "Personal Care", "18.00", "Toothpaste, soap and hygiene products"),
            "Beverages": get_or_create_category(db, "Beverages", "18.00", "Soft drinks, juices and tea"),
            "Produce": get_or_create_category(db, "Produce", "0.00", "Fresh fruit and vegetables"),
            "Bakery": get_or_create_category(db, "Bakery", "0.00", "Bread and baked goods"),
        }

        suppliers = {
            "FreshLine Distributors": get_or_create_supplier(db, "FreshLine Distributors", "Ramesh Kumar", "+91-9876543210", "orders@freshline.in", "29AAFCF1234L1Z5", "Peenya Industrial Area, Bengaluru", "Net 15", 15),
            "Daily Needs Wholesale": get_or_create_supplier(db, "Daily Needs Wholesale", "Meera Nair", "+91-9123456780", "billing@dailyneeds.in", "29AADCD9087K1Z2", "KR Market, Bengaluru", "Net 7", 7),
            "Metro FMCG Supply": get_or_create_supplier(db, "Metro FMCG Supply", "Sanjay Rao", "+91-9988776655", "supply@metrofmcg.in", "29AAACM3210Q1Z8", "Whitefield, Bengaluru", "Net 30", 30),
        }

        customers = {
            "walkin": get_or_create_customer(db, "Walk-in Loyalty Customer", "+91-9000000001", "loyalty@example.com", "Bengaluru", 20, "0.00"),
            "neha": get_or_create_customer(db, "Neha Sharma", "+91-9000000002", "neha.sharma@example.com", "Indiranagar, Bengaluru", 145, "1000.00"),
            "rohan": get_or_create_customer(db, "Rohan Mehta", "+91-9000000003", "rohan.mehta@example.com", "HSR Layout, Bengaluru", 620, "2500.00"),
            "anita": get_or_create_customer(db, "Anita Iyer", "+91-9000000004", "anita.iyer@example.com", "Jayanagar, Bengaluru", 980, "5000.00"),
            "kiran": get_or_create_customer(db, "Kiran Patel", "+91-9000000005", "kiran.patel@example.com", "Koramangala, Bengaluru", 60, "750.00"),
        }

        product_rows = [
            ("Staples", {"name": "India Gate Basmati Sella Rice 5kg", "sku": "ST-RICE-5KG", "barcode": "690225103176", "brand": "India Gate", "hsn_code": "1006", "shelf_location": "A1-Rice", "selling_price": "649.00", "cost_price": "560.00", "gst_rate": "5.00", "min_margin_percent": "12.00", "unit": "bag", "opening_quantity": "40.000", "reorder_level": "8.000", "safety_stock": "12.000", "batch_number": "RICE-APR26", "supplier_batch_code": "FL-RC-0426", "expires_in_days": 365}),
            ("Staples", {"name": "Aashirvaad Shudh Chakki Atta 5kg", "sku": "ST-ATTA-5KG", "barcode": "8901725121129", "brand": "Aashirvaad", "hsn_code": "1101", "shelf_location": "A2-Flour", "selling_price": "275.00", "cost_price": "238.00", "gst_rate": "5.00", "min_margin_percent": "10.00", "unit": "bag", "opening_quantity": "55.000", "reorder_level": "15.000", "safety_stock": "20.000", "batch_number": "ATTA-APR26", "supplier_batch_code": "DN-AT-0426", "expires_in_days": 180}),
            ("Staples", {"name": "Tata Salt 1kg", "sku": "ST-SALT-1KG", "barcode": "8904043901015", "brand": "Tata", "hsn_code": "2501", "shelf_location": "A3-Salt", "selling_price": "28.00", "cost_price": "22.00", "gst_rate": "0.00", "min_margin_percent": "18.00", "unit": "pcs", "opening_quantity": "100.000", "reorder_level": "25.000", "safety_stock": "35.000", "batch_number": "SALT-JAN26", "supplier_batch_code": "DN-SL-0126", "expires_in_days": 540}),
            ("Staples", {"name": "Fortune Sunlite Refined Sunflower Oil 1L", "sku": "ST-OIL-1L", "barcode": "8906007280242", "brand": "Fortune", "hsn_code": "1512", "shelf_location": "A4-Oil", "selling_price": "165.00", "cost_price": "145.00", "gst_rate": "5.00", "min_margin_percent": "9.00", "unit": "btl", "opening_quantity": "45.000", "reorder_level": "12.000", "safety_stock": "16.000", "batch_number": "OIL-APR26", "supplier_batch_code": "MF-OIL-0426", "expires_in_days": 240}),
            ("Dairy", {"name": "Amul Taaza Toned Milk 1L", "sku": "DA-MILK-1L", "barcode": "8901262260121", "brand": "Amul", "hsn_code": "0401", "shelf_location": "C1-Chiller", "selling_price": "68.00", "cost_price": "58.00", "gst_rate": "0.00", "min_margin_percent": "8.00", "unit": "pkt", "opening_quantity": "80.000", "reorder_level": "20.000", "safety_stock": "28.000", "batch_number": "MILK-APR30", "supplier_batch_code": "FL-MLK-0430", "expires_in_days": 4}),
            ("Dairy", {"name": "Amul Salted Butter 500g", "sku": "DA-BUTTER-500", "barcode": "8901262010023", "brand": "Amul", "hsn_code": "0405", "shelf_location": "C2-Chiller", "selling_price": "285.00", "cost_price": "252.00", "gst_rate": "12.00", "min_margin_percent": "9.00", "unit": "pcs", "opening_quantity": "12.000", "reorder_level": "15.000", "safety_stock": "18.000", "batch_number": "BUTTER-APR26", "supplier_batch_code": "FL-BTR-0426", "expires_in_days": 90}),
            ("Bakery", {"name": "Britannia Bread 400g", "sku": "BK-BREAD-400", "barcode": "8901063341500", "brand": "Britannia", "hsn_code": "1905", "shelf_location": "B1-Bakery", "selling_price": "55.00", "cost_price": "43.00", "gst_rate": "0.00", "min_margin_percent": "18.00", "unit": "pcs", "opening_quantity": "35.000", "reorder_level": "10.000", "safety_stock": "14.000", "batch_number": "BREAD-MAY01", "supplier_batch_code": "DN-BRD-0501", "expires_in_days": 5}),
            ("Snacks", {"name": "Lay's American Style Cream & Onion 52g", "sku": "SN-LAYS-52", "barcode": "8901491101837", "brand": "Lay's", "hsn_code": "1905", "shelf_location": "D2-Chips", "selling_price": "20.00", "cost_price": "15.00", "gst_rate": "12.00", "min_margin_percent": "20.00", "unit": "pcs", "opening_quantity": "120.000", "reorder_level": "30.000", "safety_stock": "40.000", "batch_number": "LAYS-MAR26", "supplier_batch_code": "MF-LY-0326", "expires_in_days": 180}),
            ("Snacks", {"name": "Parle-G Gold Biscuits 250g", "sku": "SN-PARLEG-250", "barcode": "8901719113390", "brand": "Parle", "hsn_code": "1905", "shelf_location": "D1-Biscuits", "selling_price": "35.00", "cost_price": "27.00", "gst_rate": "18.00", "min_margin_percent": "16.00", "unit": "pcs", "opening_quantity": "90.000", "reorder_level": "25.000", "safety_stock": "30.000", "batch_number": "PARLE-APR26", "supplier_batch_code": "MF-PG-0426", "expires_in_days": 210}),
            ("Household", {"name": "Surf Excel Quick Wash Detergent Powder 1kg", "sku": "HH-SURF-1KG", "barcode": "8901030681905", "brand": "Surf Excel", "hsn_code": "3402", "shelf_location": "E1-Detergent", "selling_price": "245.00", "cost_price": "210.00", "gst_rate": "18.00", "min_margin_percent": "12.00", "unit": "pcs", "opening_quantity": "30.000", "reorder_level": "8.000", "safety_stock": "10.000", "batch_number": "SURF-FEB26", "supplier_batch_code": "DN-SE-0226", "expires_in_days": 720}),
            ("Household", {"name": "Vim Dishwash Bar 300g", "sku": "HH-VIM-300", "barcode": "8901030743467", "brand": "Vim", "hsn_code": "3401", "shelf_location": "E2-Cleaning", "selling_price": "30.00", "cost_price": "23.50", "gst_rate": "18.00", "min_margin_percent": "15.00", "unit": "pcs", "opening_quantity": "70.000", "reorder_level": "20.000", "safety_stock": "25.000", "batch_number": "VIM-MAR26", "supplier_batch_code": "DN-VM-0326", "expires_in_days": 540}),
            ("Personal Care", {"name": "Colgate Strong Teeth Toothpaste 200g", "sku": "PC-COLGATE-200", "barcode": "8901314765314", "brand": "Colgate", "hsn_code": "3306", "shelf_location": "F1-Oral", "selling_price": "118.00", "cost_price": "94.00", "gst_rate": "18.00", "min_margin_percent": "16.00", "unit": "pcs", "opening_quantity": "42.000", "reorder_level": "12.000", "safety_stock": "16.000", "batch_number": "COLGATE-APR26", "supplier_batch_code": "MF-CG-0426", "expires_in_days": 720}),
            ("Personal Care", {"name": "Dettol Original Soap 125g", "sku": "PC-DETTOL-125", "barcode": "6161100956780", "brand": "Dettol", "hsn_code": "3401", "shelf_location": "F2-Soap", "selling_price": "65.00", "cost_price": "51.00", "gst_rate": "18.00", "min_margin_percent": "17.00", "unit": "pcs", "opening_quantity": "65.000", "reorder_level": "18.000", "safety_stock": "22.000", "batch_number": "DETTOL-MAR26", "supplier_batch_code": "MF-DT-0326", "expires_in_days": 600}),
            ("Beverages", {"name": "Coca-Cola Original Taste 750ml", "sku": "BV-COKE-750", "barcode": "8901764012273", "brand": "Coca-Cola", "hsn_code": "2202", "shelf_location": "G1-Drinks", "selling_price": "40.00", "cost_price": "31.00", "gst_rate": "28.00", "min_margin_percent": "15.00", "unit": "btl", "opening_quantity": "75.000", "reorder_level": "24.000", "safety_stock": "30.000", "batch_number": "COKE-APR26", "supplier_batch_code": "MF-CK-0426", "expires_in_days": 120}),
            ("Beverages", {"name": "Tata Tea Premium 250g", "sku": "BV-TATATEA-250", "barcode": "8901052005185", "brand": "Tata Tea", "hsn_code": "0902", "shelf_location": "G2-Tea", "selling_price": "145.00", "cost_price": "124.00", "gst_rate": "5.00", "min_margin_percent": "11.00", "unit": "pcs", "opening_quantity": "48.000", "reorder_level": "12.000", "safety_stock": "15.000", "batch_number": "TEA-APR26", "supplier_batch_code": "MF-TT-0426", "expires_in_days": 365}),
            ("Produce", {"name": "Robusta Banana 1kg", "sku": "PR-BANANA-1KG", "barcode": "4011", "brand": "FreshLine", "hsn_code": "0803", "shelf_location": "P1-Fruit", "selling_price": "62.00", "cost_price": "45.00", "gst_rate": "0.00", "min_margin_percent": "20.00", "unit": "kg", "opening_quantity": "25.000", "reorder_level": "12.000", "safety_stock": "15.000", "batch_number": "BANANA-TODAY", "supplier_batch_code": "FL-BN-TODAY", "expires_in_days": 3}),
        ]
        for category_name, product_data in product_rows:
            seed_product(db, admin, categories[category_name], product_data)

        ensure_open_shift(db, cashier)
        db.commit()

        product_map = products_by_sku(db)

        po1 = create_demo_purchase_order(
            db,
            admin,
            suppliers["FreshLine Distributors"],
            product_map,
            {
                "notes": "DEMO_PO_DAIRY_PRODUCE_REPLENISHMENT",
                "days_ago": 4,
                "expected_in_days": 1,
                "payment_status": "PAID",
                "items": [
                    {"sku": "DA-MILK-1L", "qty": "120.000", "unit_cost": "58.00", "gst_rate": "0.00"},
                    {"sku": "BK-BREAD-400", "qty": "45.000", "unit_cost": "43.00", "gst_rate": "0.00"},
                    {"sku": "PR-BANANA-1KG", "qty": "30.000", "unit_cost": "45.00", "gst_rate": "0.00"},
                ],
            },
        )
        receive_demo_goods(
            db,
            admin,
            po1,
            {
                "notes": "DEMO_GRN_DAIRY_PRODUCE_FULL",
                "supplier_invoice_number": "FL-INV-0426-118",
                "days_ago": 3,
                "po_payment_status": "PAID",
                "items": [
                    {"sku": "DA-MILK-1L", "qty": "120.000", "unit_cost": "58.00", "batch_number": "MILK-DEMO-01", "expires_in_days": 4},
                    {"sku": "BK-BREAD-400", "qty": "45.000", "unit_cost": "43.00", "batch_number": "BREAD-DEMO-01", "expires_in_days": 5},
                    {"sku": "PR-BANANA-1KG", "qty": "30.000", "unit_cost": "45.00", "batch_number": "BANANA-DEMO-01", "expires_in_days": 3},
                ],
            },
        )

        po2 = create_demo_purchase_order(
            db,
            admin,
            suppliers["Metro FMCG Supply"],
            product_map,
            {
                "notes": "DEMO_PO_WEEKLY_FMCG_PARTIAL",
                "days_ago": 2,
                "expected_in_days": 3,
                "payment_status": "PARTIAL",
                "items": [
                    {"sku": "SN-PARLEG-250", "qty": "120.000", "unit_cost": "27.00", "gst_rate": "18.00"},
                    {"sku": "BV-COKE-750", "qty": "90.000", "unit_cost": "31.00", "gst_rate": "28.00"},
                    {"sku": "PC-COLGATE-200", "qty": "48.000", "unit_cost": "94.00", "gst_rate": "18.00"},
                ],
            },
        )
        receive_demo_goods(
            db,
            admin,
            po2,
            {
                "notes": "DEMO_GRN_WEEKLY_FMCG_PARTIAL",
                "supplier_invoice_number": "MF-INV-0426-221",
                "days_ago": 1,
                "po_payment_status": "PARTIAL",
                "items": [
                    {"sku": "SN-PARLEG-250", "qty": "60.000", "unit_cost": "27.00", "batch_number": "PARLE-DEMO-01", "expires_in_days": 210},
                    {"sku": "BV-COKE-750", "qty": "45.000", "unit_cost": "31.00", "batch_number": "COKE-DEMO-01", "expires_in_days": 120},
                ],
            },
        )

        product_map = products_by_sku(db)
        sales = [
            {"notes": "DEMO_SALE_TODAY_001", "customer_id": customers["neha"].id, "mode": PaymentMode.UPI, "reference": "UPI-DEMO-001", "days_ago": 0, "hour": 9, "minute": 15, "lines": [{"sku": "DA-MILK-1L", "qty": "2.000"}, {"sku": "BK-BREAD-400", "qty": "1.000"}, {"sku": "SN-PARLEG-250", "qty": "2.000"}]},
            {"notes": "DEMO_SALE_TODAY_002", "customer_id": customers["rohan"].id, "mode": PaymentMode.CARD, "reference": "CARD-DEMO-8211", "days_ago": 0, "hour": 12, "minute": 40, "lines": [{"sku": "ST-RICE-5KG", "qty": "1.000", "discount": "20.00"}, {"sku": "ST-OIL-1L", "qty": "2.000"}, {"sku": "PC-DETTOL-125", "qty": "3.000"}]},
            {"notes": "DEMO_SALE_TODAY_003", "customer_id": None, "mode": PaymentMode.CASH, "days_ago": 0, "hour": 18, "minute": 5, "lines": [{"sku": "BV-COKE-750", "qty": "4.000"}, {"sku": "SN-LAYS-52", "qty": "5.000"}, {"sku": "PR-BANANA-1KG", "qty": "1.500"}]},
            {"notes": "DEMO_SALE_YESTERDAY_001", "customer_id": customers["anita"].id, "mode": PaymentMode.UPI, "reference": "UPI-DEMO-002", "days_ago": 1, "hour": 16, "minute": 30, "lines": [{"sku": "HH-SURF-1KG", "qty": "1.000"}, {"sku": "HH-VIM-300", "qty": "4.000"}, {"sku": "PC-COLGATE-200", "qty": "2.000"}]},
            {"notes": "DEMO_SALE_RETURNABLE", "customer_id": customers["kiran"].id, "mode": PaymentMode.CARD, "reference": "CARD-DEMO-4420", "days_ago": 3, "hour": 11, "minute": 25, "lines": [{"sku": "DA-BUTTER-500", "qty": "2.000"}, {"sku": "BV-TATATEA-250", "qty": "1.000"}]},
            {"notes": "DEMO_SALE_WEEKLY_BASKET", "customer_id": customers["walkin"].id, "mode": PaymentMode.CASH, "days_ago": 6, "hour": 19, "minute": 10, "lines": [{"sku": "ST-ATTA-5KG", "qty": "1.000"}, {"sku": "ST-SALT-1KG", "qty": "3.000"}, {"sku": "DA-MILK-1L", "qty": "4.000"}, {"sku": "SN-LAYS-52", "qty": "3.000"}]},
        ]
        created_sales = [create_demo_sale(db, cashier, product_map, sale_data) for sale_data in sales]

        returnable = next((sale for sale in created_sales if sale.notes == "DEMO_SALE_RETURNABLE"), None)
        if returnable and not db.scalar(select(SaleReturn).where(SaleReturn.sale_id == returnable.id)):
            sale_with_items = db.scalar(select(Sale).where(Sale.id == returnable.id).options(selectinload(Sale.items)))
            butter_item = next((item for item in sale_with_items.items if item.sku == "DA-BUTTER-500"), sale_with_items.items[0])
            returned = create_return(
                db,
                sale_with_items.id,
                SaleReturnCreate(
                    refund_mode=PaymentMode.CARD,
                    reason="Customer returned one sealed butter pack",
                    items=[ReturnItemCreate(sale_item_id=butter_item.id, quantity=Decimal("1.000"))],
                ),
                cashier,
            )
            persisted_return = db.get(SaleReturn, returned.id)
            returned_at = datetime.combine(date.today() - timedelta(days=2), time(hour=14, minute=5))
            persisted_return.created_at = returned_at
            persisted_return.updated_at = returned_at
            db.commit()

        db.commit()
        print("Seed data loaded. Admin: admin@snipymart.in / Admin@12345; Cashier: cashier@snipymart.in / Cashier@12345")
        print("Demo data includes products, batches, suppliers, customers, purchase orders, GRNs, POS sales, returns, stock movements, and loyalty points.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
