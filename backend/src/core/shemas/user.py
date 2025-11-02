from pydantic import BaseModel, EmailStr, ConfigDict
from core.security import hash_password


class CredsUserSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    email: EmailStr
    password: str


class CreateUserSchema(CredsUserSchema):
    username: str

    def to_orm(self) -> dict:
        user_data = self.model_dump()
        user_data["hashed_password"] = hash_password(user_data.pop("password"))
        return user_data


class ReadUserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)
