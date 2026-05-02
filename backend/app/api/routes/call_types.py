from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.call_type import CallTypeCreate, CallTypeResponse, CallTypeUpdate

router = APIRouter(prefix="/call-types", tags=["call-types"])


@router.get("", response_model=list[CallTypeResponse])
async def list_call_types(db: AsyncSession = Depends(get_db)) -> list[CallTypeResponse]:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("", response_model=CallTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_call_type(
    payload: CallTypeCreate, db: AsyncSession = Depends(get_db)
) -> CallTypeResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{call_type_id}", response_model=CallTypeResponse)
async def get_call_type(
    call_type_id: UUID, db: AsyncSession = Depends(get_db)
) -> CallTypeResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/{call_type_id}", response_model=CallTypeResponse)
async def update_call_type(
    call_type_id: UUID,
    payload: CallTypeUpdate,
    db: AsyncSession = Depends(get_db),
) -> CallTypeResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/{call_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_call_type(
    call_type_id: UUID, db: AsyncSession = Depends(get_db)
) -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
