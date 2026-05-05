from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from app.schemas._base import CamelResponse, CamelSchema


class InvitationCreate(CamelSchema):
    email: EmailStr


class InvitationResponse(CamelResponse):
    id: UUID
    business_id: UUID
    invited_by_id: UUID
    email: str
    expires_at: datetime
    accepted_at: datetime | None
    created_at: datetime
    invite_url: str | None = None
