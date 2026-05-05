from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from app.schemas._base import CamelResponse, CamelSchema


class ClientCreate(CamelSchema):
    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    company: str | None = None
    notes: str | None = None


class ClientUpdate(CamelSchema):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    company: str | None = None
    notes: str | None = None


class ClientResponse(CamelResponse):
    id: UUID
    business_id: UUID
    created_by_id: UUID
    full_name: str
    email: str | None
    phone: str | None
    company: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
