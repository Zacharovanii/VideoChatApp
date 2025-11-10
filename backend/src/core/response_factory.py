from fastapi import HTTPException, status
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from schemas.response import ResponseSchema, MetaInfo


def success_response(
    message: str,
    data: BaseModel | None = None,
    status_code: int = 200,
    request: Request | None = None,
) -> JSONResponse:
    payload = ResponseSchema(
        success=True,
        status="ok",
        status_code=status_code,
        message=message,
        data=data,
        meta=MetaInfo(path=request.url.path if request else None),
    ).model_dump()
    return JSONResponse(status_code=status_code, content=jsonable_encoder(payload))


def error_response(
    message: str,
    status_code: int = 400,
    errors: dict | None = None,
    request: Request | None = None,
) -> JSONResponse:
    payload = ResponseSchema(
        success=False,
        status="error",
        status_code=status_code,
        message=message,
        errors=errors,
        meta=MetaInfo(path=request.url.path if request else None),
    ).model_dump()
    return JSONResponse(status_code=status_code, content=jsonable_encoder(payload))


def error_raise(
    detail: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
):
    return HTTPException(status_code=status_code, detail=detail)


class Errors:
    INVALID_CREDENTIALS = error_raise(
        "Invalid email or password", status.HTTP_401_UNAUTHORIZED
    )
    USER_NOT_FOUND = error_raise("User not found", status.HTTP_404_NOT_FOUND)
    TOKEN_INVALID = error_raise(
        "Invalid or expired token", status.HTTP_401_UNAUTHORIZED
    )
    ACCESS_DENIED = error_raise("Access denied", status.HTTP_403_FORBIDDEN)
