from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.models.domain import (
    Category,
    InventoryBatch,
    InventoryItem,
    Product,
    StockMovement,
    StockMovementType,
    User,
)
from app.schemas.catalog import ProductCreate, ProductRead, ProductUpdate
from app.services.decimal_utils import qty


def product_to_read(product: Product) -> ProductRead:
    inventory = product.inventory
    return ProductRead(
        id=product.id,
        name=product.name,
        sku=product.sku,
        barcode=product.barcode,
        brand=product.brand,
        hsn_code=product.hsn_code,
        shelf_location=product.shelf_location,
        category_id=product.category_id,
        selling_price=product.selling_price,
        cost_price=product.cost_price,
        gst_rate=product.gst_rate,
        min_margin_percent=product.min_margin_percent,
        unit=product.unit,
        is_active=product.is_active,
        on_hand=inventory.on_hand if inventory else Decimal("0.000"),
        reorder_level=inventory.reorder_level if inventory else Decimal("0.000"),
        safety_stock=inventory.safety_stock if inventory else Decimal("0.000"),
        category_name=product.category.name if product.category else None,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


def create_product(db: Session, payload: ProductCreate, current_user: User) -> Product:
    product = Product(
        name=payload.name,
        sku=payload.sku,
        barcode=payload.barcode,
        brand=payload.brand,
        hsn_code=payload.hsn_code,
        shelf_location=payload.shelf_location,
        category_id=payload.category_id,
        selling_price=payload.selling_price,
        cost_price=payload.cost_price,
        gst_rate=payload.gst_rate,
        min_margin_percent=payload.min_margin_percent,
        unit=payload.unit,
        is_active=payload.is_active,
    )
    inventory = InventoryItem(on_hand=qty(payload.opening_quantity), reorder_level=qty(payload.reorder_level), safety_stock=qty(payload.safety_stock))
    product.inventory = inventory
    db.add(product)
    db.flush()
    if payload.opening_quantity > 0:
        batch = InventoryBatch(
            product_id=product.id,
            batch_number=payload.opening_batch_number or "OPENING",
            expiry_date=payload.opening_expiry_date,
            cost_price=payload.cost_price,
            mrp=payload.selling_price,
            received_quantity=qty(payload.opening_quantity),
            quantity_on_hand=qty(payload.opening_quantity),
        )
        db.add(batch)
        db.flush()
        db.add(
            StockMovement(
                product_id=product.id,
                batch_id=batch.id,
                movement_type=StockMovementType.ADJUSTMENT_IN,
                quantity=qty(payload.opening_quantity),
                before_quantity=Decimal("0.000"),
                after_quantity=qty(payload.opening_quantity),
                reference_type="OPENING_STOCK",
                notes="Opening stock",
                created_by_id=current_user.id,
            )
        )
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, payload: ProductUpdate) -> Product:
    data = payload.model_dump(exclude_unset=True)
    reorder_level = data.pop("reorder_level", None)
    safety_stock = data.pop("safety_stock", None)
    for key, value in data.items():
        setattr(product, key, value)
    if reorder_level is not None or safety_stock is not None:
        if not product.inventory:
            product.inventory = InventoryItem(
                on_hand=Decimal("0.000"),
                reorder_level=qty(reorder_level or Decimal("5.000")),
                safety_stock=qty(safety_stock or Decimal("0.000")),
            )
        else:
            if reorder_level is not None:
                product.inventory.reorder_level = qty(reorder_level)
            if safety_stock is not None:
                product.inventory.safety_stock = qty(safety_stock)
    db.commit()
    db.refresh(product)
    return product


def find_product_for_pos(db: Session, query: str) -> list[Product]:
    term = f"%{query.strip()}%"
    return list(
        db.scalars(
            select(Product)
            .where(
                Product.is_active.is_(True),
                or_(
                    Product.name.ilike(term),
                    Product.sku.ilike(term),
                    Product.barcode == query.strip(),
                    Product.brand.ilike(term),
                    Product.hsn_code == query.strip(),
                    Product.shelf_location.ilike(term),
                ),
            )
            .limit(20)
        )
    )


def ensure_category_exists(db: Session, category_id: int | None) -> None:
    if category_id and not db.get(Category, category_id):
        raise BusinessError("Category not found", 404)
