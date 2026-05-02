from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CallTypeBase(BaseModel):
    name: str
    description: str | None = None
    prompt_template: str


class CallTypeCreate(CallTypeBase):
    pass


class CallTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    prompt_template: str | None = None


class CallTypeResponse(CallTypeBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
