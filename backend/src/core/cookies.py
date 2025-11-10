from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from core.config import settings
from schemas import JwtPayloadSchema
from .jwt import parse_token, TOKEN_TYPE


# ===============================
# BASE COOKIE FUNCTION
# ===============================


def set_cookie(
    response: JSONResponse,
    key: str,
    value: str,
    max_age: int,
) -> None:
    """Универсальная функция для установки cookie."""
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        httponly=settings.cookie.httponly,
        secure=settings.cookie.secure,
        samesite=settings.cookie.samesite,
    )


def delete_cookie(response: JSONResponse, key: str) -> None:
    """Удаляет cookie по ключу."""
    response.delete_cookie(key)


# ===============================
# JWT COOKIES
# ===============================


def set_token_cookie(
    response: JSONResponse, token_type: TOKEN_TYPE, token: str
) -> None:
    """Устанавливает access или refresh токен в cookie."""
    if token_type == "access":
        key = settings.cookie.access_token_key
        max_age = settings.cookie.access_token_expire_second
    elif token_type == "refresh":
        key = settings.cookie.refresh_token_key
        max_age = settings.cookie.refresh_token_expire_second
    else:
        raise ValueError(f"Invalid token type: {token_type}")

    set_cookie(response, key=key, value=token, max_age=max_age)


def get_token_cookie(request: Request, token_type: TOKEN_TYPE) -> JwtPayloadSchema:
    """
    Извлекает токен указанного типа из cookie в request, декодирует и
    возвращает Pydantic модель JwtPayloadSchema.

    Бросает HTTPException(401) если токен отсутствует или недействителен.
    """
    if token_type == "access":
        cookie_key = settings.cookie.access_token_key
        missing_detail = "Access token missing"
    elif token_type == "refresh":
        cookie_key = settings.cookie.refresh_token_key
        missing_detail = "Refresh token missing"
    else:
        raise ValueError(f"Invalid token type: {token_type}")

    token = request.cookies.get(cookie_key)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=missing_detail
        )

    return parse_token(token)


def set_auth_cookies(response: JSONResponse, access: str, refresh: str) -> None:
    """Устанавливает оба токена (access + refresh)."""
    set_token_cookie(response, "access", access)
    set_token_cookie(response, "refresh", refresh)


def clear_auth_cookies(response: JSONResponse) -> None:
    delete_cookie(response, settings.cookie.access_token_key)
    delete_cookie(response, settings.cookie.refresh_token_key)
