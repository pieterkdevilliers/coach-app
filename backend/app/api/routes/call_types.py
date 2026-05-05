from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.call_type import CallType
from app.models.user import User
from app.schemas.call_type import CallTypeCreate, CallTypeResponse, CallTypeUpdate

router = APIRouter(prefix="/call-types", tags=["call-types"])


async def _get_or_404(db: AsyncSession, call_type_id: UUID, business_id: UUID) -> CallType:
    result = await db.execute(
        select(CallType).where(
            CallType.id == call_type_id,
            CallType.business_id == business_id,
            CallType.is_active.is_(True),
        )
    )
    ct = result.scalar_one_or_none()
    if not ct:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call type not found")
    return ct


@router.get("", response_model=list[CallTypeResponse])
async def list_call_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CallTypeResponse]:
    result = await db.execute(
        select(CallType)
        .where(
            CallType.business_id == current_user.business_id,
            CallType.is_active.is_(True),
        )
        .order_by(CallType.name)
    )
    return [CallTypeResponse.model_validate(ct) for ct in result.scalars().all()]


@router.post("", response_model=CallTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_call_type(
    payload: CallTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CallTypeResponse:
    ct = CallType(business_id=current_user.business_id, **payload.model_dump())
    db.add(ct)
    await db.commit()
    await db.refresh(ct)
    return CallTypeResponse.model_validate(ct)


@router.get("/{call_type_id}", response_model=CallTypeResponse)
async def get_call_type(
    call_type_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CallTypeResponse:
    ct = await _get_or_404(db, call_type_id, current_user.business_id)
    return CallTypeResponse.model_validate(ct)


@router.put("/{call_type_id}", response_model=CallTypeResponse)
async def update_call_type(
    call_type_id: UUID,
    payload: CallTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CallTypeResponse:
    ct = await _get_or_404(db, call_type_id, current_user.business_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ct, field, value)
    await db.commit()
    await db.refresh(ct)
    return CallTypeResponse.model_validate(ct)


@router.delete("/{call_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_call_type(
    call_type_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    ct = await _get_or_404(db, call_type_id, current_user.business_id)
    ct.is_active = False
    await db.commit()
