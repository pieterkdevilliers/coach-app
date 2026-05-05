from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_owner
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserResponse]:
    result = await db.execute(
        select(User).where(
            User.business_id == current_user.business_id,
            User.is_active.is_(True),
        ).order_by(User.full_name)
    )
    return [UserResponse.model_validate(u) for u in result.scalars().all()]


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_owner),
) -> UserResponse:
    user = await db.get(User, user_id)
    if not user or user.business_id != current_user.business_id or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_owner),
) -> None:
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )
    user = await db.get(User, user_id)
    if not user or user.business_id != current_user.business_id or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = False
    await db.commit()
