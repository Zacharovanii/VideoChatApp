from datetime import datetime, timedelta, UTC
from typing import Any, Literal

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException, status

from core.config import settings
from schemas.token import JwtPayloadSchema


TOKEN_TYPE = Literal["access", "refresh"]


# ===============================
# INTERNAL HELPERS
# ===============================


def _get_private_key() -> str:
    return settings.auth_jwt.private_key_path.read_text()


def _get_public_key() -> str:
    return settings.auth_jwt.public_key_path.read_text()


def _get_expiration(
    minutes: int | None = None, delta: timedelta | None = None
) -> datetime:
    now = datetime.now(UTC)
    return now + (delta or timedelta(minutes=minutes or 15))


# ===============================
# CORE JWT OPERATIONS
# ===============================


def encode_jwt(
    payload: dict[str, Any],
    private_key: str | None = None,
    algorithm: str | None = None,
    expire_minutes: int | None = None,
    expire_timedelta: timedelta | None = None,
) -> str:
    """Подписывает JWT-токен."""
    now = datetime.now(UTC)
    expire = _get_expiration(minutes=expire_minutes, delta=expire_timedelta)

    to_encode = {**payload, "exp": expire, "iat": now}

    return jwt.encode(
        to_encode,
        private_key or _get_private_key(),
        algorithm or settings.auth_jwt.algorithm,
    )


def decode_jwt(
    token: str | bytes,
    public_key: str | None = None,
    algorithm: str | None = None,
) -> dict[str, Any]:
    """Проверяет подпись и возвращает payload JWT."""
    try:
        return jwt.decode(
            token,
            public_key or _get_public_key(),
            algorithms=[algorithm or settings.auth_jwt.algorithm],
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


# ===============================
# TOKEN CREATION / VALIDATION
# ===============================


def create_token(token_type: TOKEN_TYPE, sub: str, email: str | None = None) -> str:
    """Создаёт access или refresh токен."""
    payload = JwtPayloadSchema(sub=sub, email=email, type=token_type)

    expire = (
        settings.auth_jwt.access_token_expire_minutes
        if token_type == "access"
        else settings.auth_jwt.refresh_token_expire_minutes
    )

    return encode_jwt(payload.model_dump(), expire_minutes=expire)


def parse_token(token: str) -> JwtPayloadSchema:
    """Декодирует токен и возвращает Pydantic-модель."""
    payload = decode_jwt(token)
    return JwtPayloadSchema(**payload)
