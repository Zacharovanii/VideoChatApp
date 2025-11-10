from fastapi import FastAPI
from fastapi import Request
from fastapi import status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from core.response_factory import error_response


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError | ValidationError | Exception,
) -> JSONResponse:
    validation_errors = {}
    for err in exc.errors():
        loc = ".".join(map(str, err["loc"]))
        validation_errors[loc] = err["msg"]

    return error_response(
        message="Invalid input data",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors=validation_errors,
        request=request,
    )


async def http_exception_handler(
    request: Request, exc: HTTPException | Exception
) -> JSONResponse:
    return error_response(
        message=exc.detail or "HTTP error",
        status_code=exc.status_code,
        request=request,
    )


async def generic_exception_handler(request: Request, exc: Exception):
    # не показываем traceback в проде
    return error_response(
        message="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors={"type": type(exc).__name__, "detail": str(exc)},
        request=request,
    )
