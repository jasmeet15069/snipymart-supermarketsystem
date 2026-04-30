from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.db import get_db
from app.core.deps import get_current_user, require_admin
from app.core.errors import BusinessError
from app.models.domain import Product, User
from app.schemas.catalog import ProductCreate, ProductRead, ProductUpdate
from app.services.catalog import create_product, ensure_category_exists, find_product_for_pos, product_to_read, update_product

router = APIRouter(prefix="/products", tags=["products"])


def _product_query():
    return select(Product).options(selectinload(Product.inventory), selectinload(Product.category))


@router.get("", response_model=list[ProductRead])
def list_products(
    search: str | None = None,
    active_only: bool = True,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    statement = _product_query().order_by(Product.name)
    if active_only:
        statement = statement.where(Product.is_active.is_(True))
    if search:
        term = f"%{search}%"
        statement = statement.where(or_(Product.name.ilike(term), Product.sku.ilike(term), Product.barcode.ilike(term)))
    return [product_to_read(product) for product in db.scalars(statement.limit(200))]


@router.get("/lookup", response_model=list[ProductRead])
def lookup_product(query: str = Query(min_length=1), _: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ProductRead]:
    products = find_product_for_pos(db, query)
    for product in products:
        _ = product.inventory, product.category
    return [product_to_read(product) for product in products]


@router.post("", response_model=ProductRead)
def create_product_route(payload: ProductCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)) -> ProductRead:
    ensure_category_exists(db, payload.category_id)
    product = create_product(db, payload, current_user)
    product = db.scalar(_product_query().where(Product.id == product.id))
    return product_to_read(product)


@router.patch("/{product_id}", response_model=ProductRead)
def update_product_route(product_id: int, payload: ProductUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> ProductRead:
    product = db.scalar(_product_query().where(Product.id == product_id))
    if not product:
        raise BusinessError("Product not found", 404)
    ensure_category_exists(db, payload.category_id)
    product = update_product(db, product, payload)
    product = db.scalar(_product_query().where(Product.id == product.id))
    return product_to_read(product)


@router.delete("/{product_id}", response_model=ProductRead)
def deactivate_product(product_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> ProductRead:
    product = db.scalar(_product_query().where(Product.id == product_id))
    if not product:
        raise BusinessError("Product not found", 404)
    product.is_active = False
    db.commit()
    db.refresh(product)
    return product_to_read(product)
