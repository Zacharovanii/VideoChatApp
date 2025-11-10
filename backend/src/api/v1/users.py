from typing import Annotated

from core.response_factory import success_response
from fastapi import APIRouter, Depends, HTTPException, status

from core.config import settings
from dependencies import current_user_getter as user_dependency
from core.jwt import (
    create_access_token,
    create_refresh_token,
)
from core.cookies import set_auth_cookies
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
    },
)
async def create_user(
    new_user: CreateUserSchema,
    user_crud: Annotated[UserService, Depends(user_service_getter)],
):
    user = await user_crud.create_user(user_in=new_user)
    response = success_response(
        message="User successfully created",
        status_code=status.HTTP_201_CREATED,
        data=ReadUserSchema.model_validate(user, from_attributes=True),
    )
    return response


@router.post("/login", response_model=ResponseSchema)
async def login(
    creds: CredsUserSchema,
    user_crud: UserService = Depends(user_service_getter),
):
    user = await user_crud.get_user_by_email(creds.email)
    if not user or not validate_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(sub=str(user.id), email=str(user.email))
    refresh_token = create_refresh_token(sub=str(user.id))

    response = success_response(message="Login successful")
    set_auth_cookies(response, access_token, refresh_token)

    return response


@router.get("/me", response_model=UserResponseSchema)
async def get_current_user(
    current_user: Annotated[ReadUserSchema, Depends(user_dependency)],
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
