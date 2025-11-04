from fastapi import Depends, HTTPException, Request, status
from core.security.jwt_utils import get_access_token
from api.api_v1.users.crud import UserCRUD, get_user_crud
from core.schemas.user import ReadUserSchema


async def get_current_user(
    request: Request,
    user_crud: UserCRUD = Depends(get_user_crud),
):
    payload = get_access_token(request)
    user_id = int(payload.get("sub"))
    user = await user_crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return ReadUserSchema.model_validate(user, from_attributes=True)
