from datetime import datetime
from uuid import UUID

from app.schemas._base import CamelResponse


class TranscriptResponse(CamelResponse):
    id: UUID
    recording_id: UUID
    content: str
    word_count: int | None = None
    created_at: datetime
