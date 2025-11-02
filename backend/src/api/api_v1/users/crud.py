from typing import Optional, AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User as UserORM, db_helper
from core.shemas.user import CreateUserSchema


class UserCRUD:
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
        result = await self.db.execute(select(UserORM).where(UserORM.email == email))
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> Optional[UserORM]:
        stmt = select(UserORM).filter(UserORM.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().one_or_none()


async def get_user_crud() -> AsyncGenerator[UserCRUD, None]:
    async for session in db_helper.session_getter():
        yield UserCRUD(session)
