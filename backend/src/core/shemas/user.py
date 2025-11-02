from pydantic import BaseModel, EmailStr, ConfigDict


class CreateUserShema(BaseModel):
    # model_config = ConfigDict(strict=True)

    username: str
    password: str
    email: EmailStr
