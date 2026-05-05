from datetime import datetime
from uuid import UUID

from app.schemas._base import CamelResponse


class ExtractionResponse(CamelResponse):
    id: UUID
    recording_id: UUID
    prompt_used: str
    result: dict
    call_type_id: UUID | None = None
    created_at: datetime
