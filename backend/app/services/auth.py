from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_token, decode_token, verify_password
from app.models.domain import User


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return user


def issue_token_pair(user: User) -> dict[str, str]:
    return {
        "access_token": create_token(user.email, "access"),
        "refresh_token": create_token(user.email, "refresh"),
        "token_type": "bearer",
    }


def refresh_access_token(db: Session, refresh_token: str) -> dict[str, str]:
    payload = decode_token(refresh_token, expected_type="refresh")
    user = db.scalar(select(User).where(User.email == payload.get("sub")))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return issue_token_pair(user)
