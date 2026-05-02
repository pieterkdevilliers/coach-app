from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class QueryCreate(BaseModel):
    question: str


class QueryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recording_id: UUID
    question: str
    answer: str
    created_at: datetime
