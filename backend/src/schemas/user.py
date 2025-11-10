import re

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, ValidationInfo

from core.pwd import hash_password
from .response import ResponseSchema


class CredsUserSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    email: EmailStr
    password: str


class CreateUserSchema(CredsUserSchema):
    username: str
    password_repeat: str

    def to_orm(self) -> dict:
        user_data = self.model_dump()
        user_data.pop("password_repeat")
        user_data["hashed_password"] = hash_password(user_data.pop("password"))
        return user_data

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r"^[A-Za-z0-9_-]{3,30}$", v):
            raise ValueError("Username must be 3–30 characters, letters/numbers/_/- only")
        forbidden = {"admin", "root", "system"}
        if v.lower() in forbidden:
            raise ValueError("This username is not allowed")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least one special character")
        return v


    @field_validator("password_repeat", mode="after")
    @classmethod
    def check_passwords_match(cls, value: str, info: ValidationInfo) -> str:
        if value != info.data.get("password", None):
            raise ValueError("Passwords do not match")
        return value


class ReadUserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


UserResponseSchema = ResponseSchema[ReadUserSchema]
UserListResponseSchema = ResponseSchema[list[ReadUserSchema]]
