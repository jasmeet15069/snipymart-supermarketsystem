from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.domain import Customer, Sale, User
from app.schemas.sales import SaleCreate, SaleListRow, SaleRead, SaleReturnCreate, SaleReturnRead
from app.services.sales import create_return, create_sale, get_sale

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("", response_model=SaleRead)
def create_sale_route(payload: SaleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_sale(db, payload, current_user)


@router.get("", response_model=list[SaleListRow])
def list_sales(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[SaleListRow]:
    rows = db.execute(
        select(Sale, User.full_name, Customer.name)
        .join(User, Sale.cashier_id == User.id)
        .outerjoin(Customer, Sale.customer_id == Customer.id)
        .order_by(Sale.created_at.desc())
        .limit(300)
    ).all()
    return [
        SaleListRow(
            id=sale.id,
            invoice_number=sale.invoice_number,
            status=sale.status,
            cashier_name=cashier_name,
            customer_name=customer_name,
            grand_total=sale.grand_total,
            paid_total=sale.paid_total,
            created_at=sale.created_at,
        )
        for sale, cashier_name, customer_name in rows
    ]


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale_route(sale_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_sale(db, sale_id)


@router.get("/{sale_id}/invoice", response_model=SaleRead)
def get_invoice_route(sale_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_sale(db, sale_id)


@router.post("/{sale_id}/returns", response_model=SaleReturnRead)
def create_sale_return_route(
    sale_id: int,
    payload: SaleReturnCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_return(db, sale_id, payload, current_user)
