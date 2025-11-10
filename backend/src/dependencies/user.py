from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status

from db import db_helper
from services.user import UserService
from core.jwt import get_access_token
from schemas.user import ReadUserSchema


async def user_service_getter() -> AsyncGenerator[UserService, None]:
    async for session in db_helper.session_getter():
        yield UserService(session)


async def current_user_getter(
    request: Request,
    service: UserService = Depends(user_service_getter),
):
    payload = get_access_token(request)
    user_id = int(payload.get("sub"))
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return ReadUserSchema.model_validate(user, from_attributes=True)
