from pydantic import BaseModel, EmailStr, ConfigDict

from .response import ResponseSchema

class JwtPayloadSchema(BaseModel):
    sub: str
    email: EmailStr | None = None
    type: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponseBody(BaseModel):
    access_token: str
    token_type: str = "bearer"


AccessTokenResponseSchema = ResponseSchema[TokenResponseBody]