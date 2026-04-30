from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.domain import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenPair, UserRead
from app.services.auth import authenticate_user, issue_token_pair, refresh_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    user = authenticate_user(db, payload.email, payload.password)
    return issue_token_pair(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    return refresh_access_token(db, payload.refresh_token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
