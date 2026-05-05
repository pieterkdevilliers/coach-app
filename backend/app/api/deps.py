import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user = await db.get(User, uuid.UUID(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return user


async def require_owner(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner access required")
    return current_user
