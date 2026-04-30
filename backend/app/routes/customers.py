from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.errors import BusinessError
from app.models.domain import Customer, Sale, User
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.schemas.sales import SaleListRow

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerRead])
def list_customers(search: str | None = None, _: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Customer]:
    statement = select(Customer).order_by(Customer.name)
    if search:
        term = f"%{search}%"
        statement = statement.where(or_(Customer.name.ilike(term), Customer.phone.ilike(term), Customer.email.ilike(term)))
    return list(db.scalars(statement.limit(200)))


@router.post("", response_model=CustomerRead)
def create_customer(payload: CustomerCreate, _: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Customer:
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.patch("/{customer_id}", response_model=CustomerRead)
def update_customer(customer_id: int, payload: CustomerUpdate, _: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Customer:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise BusinessError("Customer not found", 404)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", response_model=CustomerRead)
def deactivate_customer(customer_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Customer:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise BusinessError("Customer not found", 404)
    customer.is_active = False
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/{customer_id}/history", response_model=list[SaleListRow])
def customer_history(customer_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[SaleListRow]:
    rows = db.execute(
        select(Sale, User.full_name, Customer.name)
        .join(User, Sale.cashier_id == User.id)
        .outerjoin(Customer, Sale.customer_id == Customer.id)
        .where(Sale.customer_id == customer_id)
        .order_by(Sale.created_at.desc())
        .limit(100)
    ).all()
    return [
        SaleListRow(
            id=sale.id,
            invoice_number=sale.invoice_number,
            status=sale.status,
            channel=sale.channel,
            payment_status=sale.payment_status,
            cashier_name=cashier_name,
            customer_name=customer_name,
            grand_total=sale.grand_total,
            paid_total=sale.paid_total,
            created_at=sale.created_at,
        )
        for sale, cashier_name, customer_name in rows
    ]
