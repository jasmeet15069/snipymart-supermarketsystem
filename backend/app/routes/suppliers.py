from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user, require_admin
from app.core.errors import BusinessError
from app.models.domain import Supplier, User
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=list[SupplierRead])
def list_suppliers(search: str | None = None, _: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Supplier]:
    statement = select(Supplier).order_by(Supplier.name)
    if search:
        term = f"%{search}%"
        statement = statement.where(or_(Supplier.name.ilike(term), Supplier.phone.ilike(term), Supplier.email.ilike(term)))
    return list(db.scalars(statement.limit(200)))


@router.post("", response_model=SupplierRead)
def create_supplier(payload: SupplierCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> Supplier:
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.patch("/{supplier_id}", response_model=SupplierRead)
def update_supplier(supplier_id: int, payload: SupplierUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> Supplier:
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise BusinessError("Supplier not found", 404)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(supplier, key, value)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", response_model=SupplierRead)
def deactivate_supplier(supplier_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> Supplier:
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise BusinessError("Supplier not found", 404)
    supplier.is_active = False
    db.commit()
    db.refresh(supplier)
    return supplier
