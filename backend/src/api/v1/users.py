from typing import Annotated

from core.response_factory import success_response
from fastapi import APIRouter, Depends, HTTPException, status

from core.config import settings
from dependencies import current_user_getter
from core.jwt import create_token
from core.cookies import set_auth_cookies, clear_auth_cookies
from core.pwd import validate_password
from schemas import (
    CreateUserSchema,
    ReadUserSchema,
    CredsUserSchema,
    UserResponseSchema,
    ResponseSchema,
)
from services.user import UserService
from dependencies.user import user_service_getter

router = APIRouter(prefix=settings.api.v1.users, tags=["Users"])


@router.post(
    "/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": ResponseSchema, "description": "User successfully created"},
        409: {
            "model": ResponseSchema,
            "description": "Username or email already in used",
        },
    },
)
async def create_user(
    new_user: CreateUserSchema,
    service: Annotated[UserService, Depends(user_service_getter)],
):
    try:
        user = await service.create_user(user_in=new_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    response = success_response(
        message="User successfully created",
        status_code=status.HTTP_201_CREATED,
        data=ReadUserSchema.model_validate(user, from_attributes=True),
    )

    access_token = create_token(token_type="access", sub=str(user.id))
    refresh_token = create_token(token_type="refresh", sub=str(user.id))
    set_auth_cookies(response, access_token, refresh_token)

    return response


@router.post("/login", response_model=ResponseSchema)
async def login(
    creds: CredsUserSchema,
    service: UserService = Depends(user_service_getter),
):
    user = await service.get_user_by(condition="email", value=str(creds.email))
    if not user or not validate_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token(token_type="access", sub=str(user.id))
    refresh_token = create_token(token_type="refresh", sub=str(user.id))

    response = success_response(message="Login successful")
    set_auth_cookies(response, access_token, refresh_token)

    return response


@router.get("/me", response_model=UserResponseSchema)
async def get_current_user(
    current_user: Annotated[ReadUserSchema, Depends(current_user_getter)],
):
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    response = success_response(
        message="Successfully get current user info",
        data=current_user,
    )
    return response


@router.get("/logout", response_model=UserResponseSchema)
async def logout(
    current_user: Annotated[ReadUserSchema, Depends(current_user_getter)],
):
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    response = success_response(
        message="Successfully logout",
        data=current_user,
    )
    clear_auth_cookies(response=response)
    return response
