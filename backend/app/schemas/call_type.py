from datetime import datetime
from uuid import UUID

from app.schemas._base import CamelResponse, CamelSchema


class CallTypeBase(CamelSchema):
    name: str
    description: str | None = None
    prompt_template: str


class CallTypeCreate(CallTypeBase):
    pass


class CallTypeUpdate(CamelSchema):
    name: str | None = None
    description: str | None = None
    prompt_template: str | None = None


class CallTypeResponse(CamelResponse):
    id: UUID
    business_id: UUID
    name: str
    description: str | None = None
    prompt_template: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
