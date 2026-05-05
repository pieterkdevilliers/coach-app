from datetime import datetime
from uuid import UUID

from app.schemas._base import CamelResponse, CamelSchema


class ActionStepCreate(CamelSchema):
    description: str
    sort_order: int = 0


class ActionStepUpdate(CamelSchema):
    description: str | None = None
    is_complete: bool | None = None
    sort_order: int | None = None


class ActionStepResponse(CamelResponse):
    id: UUID
    call_id: UUID
    description: str
    is_complete: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
