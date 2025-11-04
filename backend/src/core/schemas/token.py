from pydantic import BaseModel, EmailStr


class JwtPayloadShema(BaseModel):
    sub: str
    email: EmailStr | None = None
    type: str