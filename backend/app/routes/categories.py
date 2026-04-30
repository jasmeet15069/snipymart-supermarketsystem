from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user, require_admin
from app.core.errors import BusinessError
from app.models.domain import Category, User
from app.schemas.catalog import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name)))


@router.post("", response_model=CategoryRead)
def create_category(payload: CategoryCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> Category:
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, payload: CategoryUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> Category:
    category = db.get(Category, category_id)
    if not category:
        raise BusinessError("Category not found", 404)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", response_model=CategoryRead)
def deactivate_category(category_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> Category:
    category = db.get(Category, category_id)
    if not category:
        raise BusinessError("Category not found", 404)
    category.is_active = False
    db.commit()
    db.refresh(category)
    return category
