"""Recording processing orchestration."""

import logging
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.recording import Recording, RecordingStatus

logger = logging.getLogger(__name__)


def build_file_path(recording_id: uuid.UUID, filename: str) -> Path:
    return Path(settings.file_storage_path) / str(recording_id) / filename


async def save_upload(
    recording_id: uuid.UUID,
    filename: str,
    data: bytes,
) -> Path:
    dest = build_file_path(recording_id, filename)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dest


async def update_status(
    db: AsyncSession,
    recording: Recording,
    status: RecordingStatus,
    *,
    scribe_job_id: str | None = None,
    error_message: str | None = None,
) -> None:
    recording.status = status
    if scribe_job_id is not None:
        recording.scribe_job_id = scribe_job_id
    if error_message is not None:
        recording.error_message = error_message
    await db.commit()
