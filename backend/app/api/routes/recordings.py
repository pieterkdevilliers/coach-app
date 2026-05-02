from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.recording import RecordingResponse
from app.schemas.transcript import TranscriptResponse
from app.schemas.extraction import ExtractionResponse

router = APIRouter(prefix="/recordings", tags=["recordings"])


@router.get("", response_model=list[RecordingResponse])
async def list_recordings(db: AsyncSession = Depends(get_db)) -> list[RecordingResponse]:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post(
    "/upload",
    response_model=RecordingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_recording(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
) -> RecordingResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: UUID, db: AsyncSession = Depends(get_db)
) -> RecordingResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/{recording_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recording(
    recording_id: UUID, db: AsyncSession = Depends(get_db)
) -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/{recording_id}/reprocess", response_model=RecordingResponse)
async def reprocess_recording(
    recording_id: UUID, db: AsyncSession = Depends(get_db)
) -> RecordingResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
