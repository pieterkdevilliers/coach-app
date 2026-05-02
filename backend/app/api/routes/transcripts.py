from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.transcript import TranscriptResponse

router = APIRouter(prefix="/recordings", tags=["transcripts"])


@router.get("/{recording_id}/transcript", response_model=TranscriptResponse)
async def get_transcript(
    recording_id: UUID, db: AsyncSession = Depends(get_db)
) -> TranscriptResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
