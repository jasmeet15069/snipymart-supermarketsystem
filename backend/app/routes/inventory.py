from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.domain import Product, StockMovement, User
from app.schemas.catalog import InventoryBatchRead, InventoryRow, StockMovementRead

router = APIRouter(prefix="/inventory", tags=["inventory"])


def _inventory_rows(db: Session, low_only: bool = False) -> list[InventoryRow]:
    statement = (
        select(Product)
        .options(selectinload(Product.inventory), selectinload(Product.batches))
        .where(Product.is_active.is_(True))
        .order_by(Product.name)
    )
    rows: list[InventoryRow] = []
    for product in db.scalars(statement):
        if not product.inventory:
            continue
        is_low = product.inventory.on_hand < product.inventory.reorder_level
        if low_only and not is_low:
            continue
        rows.append(
            InventoryRow(
                product_id=product.id,
                product_name=product.name,
                sku=product.sku,
                barcode=product.barcode,
                on_hand=product.inventory.on_hand,
                reorder_level=product.inventory.reorder_level,
                is_low_stock=is_low,
                batches=[
                    InventoryBatchRead.model_validate(batch)
                    for batch in product.batches
                    if batch.quantity_on_hand > 0
                ],
            )
        )
    return rows


@router.get("", response_model=list[InventoryRow])
def list_inventory(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[InventoryRow]:
    return _inventory_rows(db)


@router.get("/alerts", response_model=list[InventoryRow])
def low_stock_alerts(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[InventoryRow]:
    return _inventory_rows(db, low_only=True)


@router.get("/movements", response_model=list[StockMovementRead])
def list_movements(product_id: int | None = None, _: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[StockMovementRead]:
    statement = select(StockMovement).join(StockMovement.product).order_by(StockMovement.created_at.desc()).limit(300)
    if product_id:
        statement = statement.where(StockMovement.product_id == product_id)
    movements = db.scalars(statement).all()
    return [
        StockMovementRead(
            id=movement.id,
            product_id=movement.product_id,
            product_name=movement.product.name if movement.product else None,
            batch_id=movement.batch_id,
            movement_type=movement.movement_type.value,
            quantity=movement.quantity,
            before_quantity=movement.before_quantity,
            after_quantity=movement.after_quantity,
            reference_type=movement.reference_type,
            reference_id=movement.reference_id,
            notes=movement.notes,
            created_at=movement.created_at,
        )
        for movement in movements
    ]
