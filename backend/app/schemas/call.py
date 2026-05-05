from datetime import datetime
from uuid import UUID

from app.models.call import CallStatus
from app.schemas._base import CamelResponse, CamelSchema


class CallCreate(CamelSchema):
    title: str
    call_type_id: UUID
    called_at: datetime
    duration_seconds: int | None = None
    notes: str | None = None


class CallUpdate(CamelSchema):
    title: str | None = None
    call_type_id: UUID | None = None
    called_at: datetime | None = None
    duration_seconds: int | None = None
    notes: str | None = None


class RecordingInCall(CamelResponse):
    id: UUID
    file_name: str
    s3_key: str | None
    scribe_job_id: str | None
    error_message: str | None
    created_at: datetime


class TranscriptInCall(CamelResponse):
    id: UUID
    content: str
    word_count: int | None
    updated_at: datetime


class SummaryInCall(CamelResponse):
    id: UUID
    content: str
    updated_at: datetime


class ActionStepInCall(CamelResponse):
    id: UUID
    description: str
    is_complete: bool
    sort_order: int
    created_at: datetime


class CallResponse(CamelResponse):
    id: UUID
    business_id: UUID
    client_id: UUID
    call_type_id: UUID
    created_by_id: UUID
    title: str
    called_at: datetime
    duration_seconds: int | None
    notes: str | None
    status: CallStatus
    created_at: datetime
    updated_at: datetime
    recording: RecordingInCall | None = None
    transcript: TranscriptInCall | None = None
    summary: SummaryInCall | None = None
    action_steps: list[ActionStepInCall] = []


class CallListResponse(CamelResponse):
    id: UUID
    call_type_id: UUID
    title: str
    called_at: datetime
    status: CallStatus
    has_recording: bool = False
    has_transcript: bool = False
    has_summary: bool = False
    action_steps_total: int = 0
    action_steps_complete: int = 0
