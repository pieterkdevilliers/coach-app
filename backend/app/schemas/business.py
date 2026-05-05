from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from app.schemas._base import CamelResponse


class BusinessResponse(CamelResponse):
    id: UUID
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
