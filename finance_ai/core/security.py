# finance_ai/core/security.py
from __future__ import annotations

import datetime as dt
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from finance_ai.core.settings import settings

# Use Argon2 for password hashing (robust & modern)
# Params are sensible defaults; you can tune memory_cost/time_cost if needed.
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=102400,  # ~100 MiB
    argon2__time_cost=2,
    argon2__parallelism=8,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _jwt_secret() -> str:
    """
    Resolve the JWT secret key. Prefer JWT_SECRET_KEY if set; otherwise fallback to SECRET_KEY.
    """
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