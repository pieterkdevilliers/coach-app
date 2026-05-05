from datetime import datetime
from uuid import UUID

from app.schemas._base import CamelResponse, CamelSchema


class RecordingCreate(CamelSchema):
    file_name: str


class RecordingResponse(CamelResponse):
    id: UUID
    call_id: UUID
    business_id: UUID
    file_name: str
    s3_key: str | None
    scribe_job_id: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
