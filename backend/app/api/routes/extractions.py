from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.extraction import ExtractionResponse

router = APIRouter(prefix="/recordings", tags=["extractions"])


@router.get("/{recording_id}/extraction", response_model=ExtractionResponse)
async def get_extraction(
    recording_id: UUID, db: AsyncSession = Depends(get_db)
) -> ExtractionResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
