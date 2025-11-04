from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status

from core.security.cookie_utils import set_auth_cookies
from core.security.jwt_utils import *
from core.security.pwd_utils import *
from core.utils.response_factory import success_response
from core.shemas.user import (
    CreateUserSchema,
    ReadUserSchema,
    CredsUserSchema,
    UserResponseShema,
)
from core.shemas.response import ResponseSchema
from .crud import get_user_crud, UserCRUD


router = APIRouter(prefix=settings.api.v1.users)


@router.post("/register", response_model=UserResponseShema)
async def create_user(
    new_user: CreateUserSchema,
    user_crud: Annotated[UserCRUD, Depends(get_user_crud)],
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
    user_crud: UserCRUD = Depends(get_user_crud),
):
    user = await user_crud.get_user_by_email(creds.email)
    if not user or not validate_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(sub=str(user.id), email=str(user.email))
    refresh_token = create_refresh_token(sub=str(user.id))

    response = success_response(message="Login successful")
    set_auth_cookies(response, access_token, refresh_token)

    return response


@router.get("/me", response_model=ReadUserSchema)
async def get_current_user(
    request: Request,
    user_crud: Annotated[UserCRUD, Depends(get_user_crud)],
):
    payload = get_access_token(request)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await user_crud.get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
