from pydantic import BaseModel, EmailStr, ConfigDict


class JwtPayloadSchema(BaseModel):
    sub: str
    email: EmailStr | None = None
    type: str

    model_config = ConfigDict(from_attributes=True)