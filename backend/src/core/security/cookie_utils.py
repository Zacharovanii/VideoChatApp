from core.config import settings
from fastapi.responses import JSONResponse


def set_jwt_cookie(
    response: JSONResponse,
    cookie_key: str,
    cookie_content: str,
    cookie_age: int,
) -> None:
    response.set_cookie(
        key=cookie_key,
        value=cookie_content,
        httponly=settings.cookie.httponly,
        samesite=settings.cookie.samesite,
        secure=settings.cookie.secure,
        max_age=cookie_age,
    )


def set_jwt_access_cookie(
    response: JSONResponse,
    access: str,
) -> None:
    set_jwt_cookie(
        response,
        cookie_key=settings.cookie.access_token_key,
        cookie_content=access,
        cookie_age=settings.cookie.access_token_expire_second,
    )


def set_jwt_refresh_cookie(
    response: JSONResponse,
    refresh: str,
) -> None:
    set_jwt_cookie(
        response,
        cookie_key=settings.cookie.refresh_token_key,
        cookie_content=refresh,
        cookie_age=settings.cookie.refresh_token_expire_second,
    )


def set_auth_cookies(response: JSONResponse, access: str, refresh: str) -> None:
    set_jwt_access_cookie(response, access)
    set_jwt_refresh_cookie(response, refresh)


def clear_auth_cookies(response: JSONResponse) -> None:
    response.delete_cookie(settings.cookie.access_token_key)
    response.delete_cookie(settings.cookie.refresh_token_key)
