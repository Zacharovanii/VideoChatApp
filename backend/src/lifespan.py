from contextlib import asynccontextmanager

from fastapi import FastAPI

from db import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db_helper.dispose()
