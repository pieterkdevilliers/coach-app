from datetime import datetime
from uuid import UUID

from app.models.recording import RecordingStatus
from app.schemas._base import CamelResponse, CamelSchema


class RecordingCreate(CamelSchema):
    title: str
    call_type_id: UUID
    client_id: UUID
    client_name: str | None = None
    recorded_at: datetime | None = None


class RecordingResponse(CamelResponse):
    id: UUID
    business_id: UUID
    client_id: UUID
    created_by_id: UUID
    call_type_id: UUID
    title: str
    client_name: str | None = None
    recorded_at: datetime | None = None
    file_name: str
    file_path: str
    duration_seconds: int | None = None
    status: RecordingStatus
    scribe_job_id: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
