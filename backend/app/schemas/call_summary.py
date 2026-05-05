from datetime import datetime
from uuid import UUID

from app.schemas._base import CamelResponse, CamelSchema


class CallSummaryUpsert(CamelSchema):
    content: str


class CallSummaryResponse(CamelResponse):
    id: UUID
    call_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime
