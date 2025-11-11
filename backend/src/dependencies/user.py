from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status

from core.jwt import decode_jwt
from db import db_helper
from services.user import UserService
from schemas.user import ReadUserSchema
from jwt import ExpiredSignatureError, InvalidTokenError


async def user_service_getter() -> AsyncGenerator[UserService, None]:
    async for session in db_helper.session_getter():
        yield UserService(session)


async def is_authorized(request: Request) -> tuple[int, str]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header.split(" ")[1]

    try:
        payload = decode_jwt(token)
    except (ExpiredSignatureError, InvalidTokenError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return user_id, email


async def current_user_getter(
    service: UserService = Depends(user_service_getter),
    payload: tuple[int, str] = Depends(is_authorized),
):
    user_id = payload[0]

    user = await service.get_user_by("id", int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return ReadUserSchema.model_validate(user, from_attributes=True)
