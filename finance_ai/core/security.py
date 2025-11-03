# finance_ai/core/security.py
from __future__ import annotations

import datetime as dt
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from finance_ai.core.settings import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=102400,
    argon2__time_cost=2,
    argon2__parallelism=8,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _jwt_secret() -> str:
    return settings.JWT_SECRET_KEY or settings.SECRET_KEY  # type: ignore[attr-defined]


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    expire_delta = expires_minutes or settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    expire = dt.datetime.utcnow() + dt.timedelta(minutes=expire_delta)
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, _jwt_secret(), algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None