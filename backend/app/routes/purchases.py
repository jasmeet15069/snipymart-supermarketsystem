from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_admin
from app.models.domain import PurchaseOrder, Supplier, User
from app.schemas.purchases import (
    GoodsReceiptCreate,
    GoodsReceiptRead,
    PurchaseOrderCreate,
    PurchaseOrderListRow,
    PurchaseOrderRead,
)
from app.services.purchases import create_purchase_order, get_purchase_order, receive_goods

router = APIRouter(prefix="/purchase-orders", tags=["purchases"], dependencies=[Depends(require_admin)])


@router.post("", response_model=PurchaseOrderRead)
def create_po_route(payload: PurchaseOrderCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return create_purchase_order(db, payload, current_user)


@router.get("", response_model=list[PurchaseOrderListRow])
def list_purchase_orders(db: Session = Depends(get_db)) -> list[PurchaseOrderListRow]:
    rows = db.execute(
        select(PurchaseOrder, Supplier.name)
        .join(Supplier, PurchaseOrder.supplier_id == Supplier.id)
        .order_by(PurchaseOrder.created_at.desc())
        .limit(200)
    ).all()
    return [
        PurchaseOrderListRow(
            id=po.id,
            po_number=po.po_number,
            supplier_name=supplier_name,
            status=po.status,
            payment_status=po.payment_status,
            grand_total=po.grand_total,
            expected_date=po.expected_date,
            created_at=po.created_at,
        )
        for po, supplier_name in rows
    ]


@router.get("/{po_id}", response_model=PurchaseOrderRead)
def get_po_route(po_id: int, db: Session = Depends(get_db)):
    return get_purchase_order(db, po_id)


@router.post("/{po_id}/receive", response_model=GoodsReceiptRead)
def receive_po_route(po_id: int, payload: GoodsReceiptCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return receive_goods(db, po_id, payload, current_user)
