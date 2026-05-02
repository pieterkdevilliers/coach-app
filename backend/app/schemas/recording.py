from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.recording import RecordingStatus


class RecordingBase(BaseModel):
    title: str
    call_type_id: UUID
    client_name: str | None = None
    recorded_at: datetime | None = None


class RecordingCreate(RecordingBase):
    pass


class RecordingResponse(RecordingBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_name: str
    file_path: str
    duration_seconds: int | None = None
    status: RecordingStatus
    scribe_job_id: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
