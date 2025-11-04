from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from core.shemas.response import ResponseSchema, MetaInfo
from fastapi import Request
from pydantic import BaseModel


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
    return JSONResponse(status_code=status_code, content=payload)
