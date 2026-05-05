from datetime import datetime
from uuid import UUID

from app.schemas._base import CamelResponse, CamelSchema


class ClientNoteCreate(CamelSchema):
    content: str


class ClientNoteResponse(CamelResponse):
    id: UUID
    client_id: UUID
    business_id: UUID
    created_by_id: UUID
    created_by_name: str
    content: str
    created_at: datetime
