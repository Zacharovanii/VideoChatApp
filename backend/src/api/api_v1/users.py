from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from api.api_v1.crud.users import get_all_users
from api.api_v1.crud.users import create_user as users_crud
from core.models import db_helper
from core.shemas.user import UserRead, UserCreate

router = APIRouter(tags=["Users"])


@router.get("/users", response_model=list[UserRead])
async def get_users(session: AsyncSession = Depends(db_helper.session_getter)):
    users = await get_all_users(session=session)
    return users


@router.post("/users", response_model=UserRead)
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    user = await users_crud(session=session, user_create=user)
    return user
