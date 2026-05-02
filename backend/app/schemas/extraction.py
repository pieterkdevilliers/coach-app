from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExtractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recording_id: UUID
    prompt_used: str
    result: dict
    call_type_id: UUID | None = None
    created_at: datetime
