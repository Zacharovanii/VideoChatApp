from typing import Optional, AsyncGenerator

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User, db_helper
from core.security import hash_password


class UserCRUD:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_user(self, username: str, email: str, password: str) -> User:
        hashed_pwd = hash_password(password)
        new_user = User(username=username, email=email, hashed_password=hashed_pwd)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
    ) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        if not user:
            return None

        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.hashed_password = hash_password(password).decode()
        if is_active is not None:
            user.is_active = is_active
        if is_verified is not None:
            user.is_verified = is_verified

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        if not user:
            return False

        await self.db.delete(user)
        await self.db.commit()
        return True


async def get_user_crud() -> AsyncGenerator[UserCRUD, None]:
    async for session in db_helper.session_getter():
        yield UserCRUD(session)
