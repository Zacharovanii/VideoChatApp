from pydantic import BaseModel, Field
from typing import Any, Optional, Generic, TypeVar
from datetime import datetime, UTC


T = TypeVar("T")


class MetaInfo(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    path: Optional[str] = None


class ResponseSchema(BaseModel, Generic[T]):
    success: bool
    status: str
    status_code: int
    message: str
    data: Optional[T] = None
    errors: Optional[dict] = None
    meta: MetaInfo = Field(default_factory=MetaInfo)
