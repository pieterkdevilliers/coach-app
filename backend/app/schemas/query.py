from datetime import datetime
from uuid import UUID

from app.schemas._base import CamelResponse, CamelSchema


class QueryCreate(CamelSchema):
    question: str


class QueryResponse(CamelResponse):
    id: UUID
    recording_id: UUID
    question: str
    answer: str
    created_at: datetime
