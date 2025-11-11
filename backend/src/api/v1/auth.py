from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from core.config import settings
from core.cookies import set_cookie
from core.response_factory import success_response
from schemas import CredsUserSchema, ResponseSchema
from schemas.token import AccessTokenResponseSchema, TokenResponseBody
from services.user import UserService
from core.jwt import create_token
from dependencies.user import user_service_getter

router = APIRouter(prefix=settings.api.v1.auth, tags=["Auth"])


@router.post(
    "/login",
    response_model=AccessTokenResponseSchema,
    responses={401: {"model": ResponseSchema, "description": "UNAUTHORIZED"}},
)
async def login(
    credentials: CredsUserSchema,
    service: Annotated[UserService, Depends(user_service_getter)],
):
    try:
        user = await service.verify_user(str(credentials.email), credentials.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong email or password"
        )

    access = create_token(
        token_type="access",
        sub=str(user.id),
        email=user.email,
    )

    refresh = create_token(
        token_type="refresh",
        sub=str(user.id),
    )

    response = success_response(
        status_code=status.HTTP_200_OK,
        message="Login successful",
        data=TokenResponseBody(access_token=access),
    )

    set_cookie(
        response,
        settings.cookie.refresh_token_key,
        refresh,
        settings.cookie.refresh_token_expire_second,
    )

    return response


@router.post("/refresh")
async def refresh_token() -> None:
    pass


@router.post("/profile")
async def profile() -> None:
    pass


@router.post("/logout")
async def logout() -> None:
    pass
