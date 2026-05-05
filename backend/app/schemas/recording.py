from datetime import datetime
from uuid import UUID

from app.schemas._base import CamelResponse, CamelSchema


class PresignUploadRequest(CamelSchema):
    file_name: str
    content_type: str


class PresignUploadResponse(CamelSchema):
    upload_url: str
    s3_key: str
    expires_in: int


class RecordingConfirmRequest(CamelSchema):
    s3_key: str
    file_name: str


class RecordingConfirmResponse(CamelResponse):
    id: UUID
    call_id: UUID
    file_name: str
    s3_key: str
    presigned_read_url: str
    created_at: datetime


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
