from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import User as UserORM
from schemas import CreateUserSchema


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_user(
        self,
        user_in: CreateUserSchema,
    ) -> UserORM:
        new_user = UserORM(**user_in.to_orm())
        self.db.add(new_user)

        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user

    async def get_user_by_email(self, email: str) -> Optional[UserORM]:
        stmt = select(UserORM).filter(UserORM.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[UserORM]:
        stmt = select(UserORM).filter(UserORM.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().one_or_none()
