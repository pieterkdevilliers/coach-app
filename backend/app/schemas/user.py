from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from app.models.user import UserRole
from app.schemas._base import CamelResponse, CamelSchema


class UserResponse(CamelResponse):
    id: UUID
    business_id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(CamelSchema):
    full_name: str | None = None
    role: UserRole | None = None


class MeResponse(CamelResponse):
    id: UUID
    business_id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
