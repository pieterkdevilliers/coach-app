from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TranscriptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recording_id: UUID
    content: str
    word_count: int | None = None
    created_at: datetime
