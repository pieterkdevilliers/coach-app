from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.query import QueryCreate, QueryResponse

router = APIRouter(prefix="/recordings", tags=["queries"])


@router.post(
    "/{recording_id}/queries",
    response_model=QueryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_query(
    recording_id: UUID,
    payload: QueryCreate,
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{recording_id}/queries", response_model=list[QueryResponse])
async def list_queries(
    recording_id: UUID, db: AsyncSession = Depends(get_db)
) -> list[QueryResponse]:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
