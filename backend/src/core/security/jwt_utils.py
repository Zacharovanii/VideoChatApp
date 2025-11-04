from datetime import datetime, timedelta, UTC

import jwt

from core.config import settings
from core.shemas.token import JwtPayloadShema

from fastapi import Request
from fastapi import HTTPException


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def create_access_token(sub: str, email: str | None = None) -> str:
    payload = JwtPayloadShema(sub=sub, email=email, type="access")
    return encode_jwt(payload=payload.model_dump())


def create_refresh_token(sub: str, email: str | None = None) -> str:
    payload = JwtPayloadShema(sub=sub, email=email, type="refresh")
    return encode_jwt(
        payload=payload.model_dump(),
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


def get_access_token(request: Request) -> dict:
    token = request.cookies.get(settings.cookie.access_token_key)
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")

    try:
        payload = decode_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


def get_refresh_token(request: Request) -> str:
    return request.cookies.get(settings.cookie.refresh_token_key)
