from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from core.security import *
from core.shemas.user import CreateUserSchema, ReadUserSchema, CredsUserSchema
from .crud import get_user_crud, UserCRUD


router = APIRouter(prefix=settings.api.v1.users)


@router.post("/register", response_model=ReadUserSchema)
async def create_user(
    new_user: CreateUserSchema,
    user_crud: Annotated[UserCRUD, Depends(get_user_crud)],
):
    user = await user_crud.create_user(user_in=new_user)
    return user


@router.post("/login")
async def login(
    creds: CredsUserSchema,
    user_crud: UserCRUD = Depends(get_user_crud),
):
    user = await user_crud.get_user_by_email(creds.email)
    if not user or not validate_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,  # True на продакшене
        max_age=60 * 15,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )
    return response


@router.get("/me", response_model=ReadUserSchema)
async def get_current_user(
    request: Request,
    user_crud: Annotated[UserCRUD, Depends(get_user_crud)],
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")

    try:
        payload = decode_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await user_crud.get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
