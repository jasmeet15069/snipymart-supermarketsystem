from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_admin
from app.core.errors import BusinessError
from app.core.security import hash_password
from app.models.domain import User
from app.schemas.auth import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    return list(db.scalars(select(User).order_by(User.full_name)))


@router.post("", response_model=UserRead)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_active=payload.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if not user:
        raise BusinessError("User not found", 404)
    data = payload.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    for key, value in data.items():
        setattr(user, key, value)
    if password:
        user.hashed_password = hash_password(password)
    db.commit()
    db.refresh(user)
    return user
