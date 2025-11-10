import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router as api_router
from core.config import settings
from exceptions import register_exception_handlers
from lifespan import lifespan
from schemas import ResponseSchema


app = FastAPI(
    lifespan=lifespan,
    title="VideoChat API",
    responses={
        422: {"model": ResponseSchema, "description": "Validation Error"},
        400: {"model": ResponseSchema, "description": "Bad Request"},
        500: {"model": ResponseSchema, "description": "Internal Server Error"},
    },
)

app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)

register_exception_handlers(app)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.run.host, port=settings.run.port, reload=True)
