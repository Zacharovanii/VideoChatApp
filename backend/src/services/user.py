from typing import Optional, Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import User as UserORM
from schemas import CreateUserSchema

search_by = Literal["email", "id", "username"]


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_user(
        self,
        user_in: CreateUserSchema,
    ) -> UserORM:
        # Проверка занятости email
        existing_email = await self.get_user_by("email", str(user_in.email))
        if existing_email:
            raise ValueError("Email already in use")

        # Проверка занятости username
        existing_username = await self.get_user_by("username", user_in.username)
        if existing_username:
            raise ValueError("Username already in use")

        new_user = UserORM(**user_in.to_orm())
        self.db.add(new_user)

        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user

    async def get_user_by(
        self,
        condition: search_by,
        value: str | int,
    ) -> Optional[UserORM]:
        if condition == "id" and not isinstance(value, int):
            raise ValueError("Id must be int")

        column_map = {
            "email": UserORM.email,
            "id": UserORM.id,
            "username": UserORM.username,
        }
        stmt = select(UserORM).filter(column_map[condition] == value)
        result = await self.db.execute(stmt)
        return result.scalars().one_or_none()
