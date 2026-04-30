from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"
TokenType = Literal["access", "refresh"]


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_token(subject: str, token_type: TokenType, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        minutes = settings.access_token_expire_minutes if token_type == "access" else settings.refresh_token_expire_minutes
        expires_delta = timedelta(minutes=minutes)
    now = datetime.now(UTC)
    payload: dict[str, Any] = {"sub": subject, "type": token_type, "iat": now, "exp": now + expires_delta}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str, expected_type: TokenType = "access") -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc
    if payload.get("type") != expected_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    return payload
