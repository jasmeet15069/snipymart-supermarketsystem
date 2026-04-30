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
        category_id=product.category_id,
        selling_price=product.selling_price,
        cost_price=product.cost_price,
        gst_rate=product.gst_rate,
        unit=product.unit,
        is_active=product.is_active,
        on_hand=inventory.on_hand if inventory else Decimal("0.000"),
        reorder_level=inventory.reorder_level if inventory else Decimal("0.000"),
        category_name=product.category.name if product.category else None,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


def create_product(db: Session, payload: ProductCreate, current_user: User) -> Product:
    product = Product(
        name=payload.name,
        sku=payload.sku,
        barcode=payload.barcode,
        category_id=payload.category_id,
        selling_price=payload.selling_price,
        cost_price=payload.cost_price,
        gst_rate=payload.gst_rate,
        unit=payload.unit,
        is_active=payload.is_active,
    )
    inventory = InventoryItem(on_hand=qty(payload.opening_quantity), reorder_level=qty(payload.reorder_level))
    product.inventory = inventory
    db.add(product)
    db.flush()
    if payload.opening_quantity > 0:
        batch = InventoryBatch(
            product_id=product.id,
            batch_number=payload.opening_batch_number or "OPENING",
            expiry_date=payload.opening_expiry_date,
            cost_price=payload.cost_price,
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
    for key, value in data.items():
        setattr(product, key, value)
    if reorder_level is not None:
        if not product.inventory:
            product.inventory = InventoryItem(on_hand=Decimal("0.000"), reorder_level=qty(reorder_level))
        else:
            product.inventory.reorder_level = qty(reorder_level)
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
                or_(Product.name.ilike(term), Product.sku.ilike(term), Product.barcode == query.strip()),
            )
            .limit(20)
        )
    )


def ensure_category_exists(db: Session, category_id: int | None) -> None:
    if category_id and not db.get(Category, category_id):
        raise BusinessError("Category not found", 404)
