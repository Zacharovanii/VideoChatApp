import uvicorn

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from core.config import settings
from core.models import db_helper
from core.middleware.error_handler import ErrorHandlerMiddleware
from core.utils.response_factory import error_response

from api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db_helper.dispose()


main_app = FastAPI(lifespan=lifespan, title="VideoChat API")

main_app.include_router(api_router)
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)


@main_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
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


@main_app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(
        message=exc.detail or "HTTP error",
        status_code=exc.status_code,
        request=request,
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app", host=settings.run.host, port=settings.run.port, reload=True
    )
