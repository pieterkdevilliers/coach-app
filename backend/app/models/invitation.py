import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("businesses.id"), nullable=False, index=True
    )
    invited_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
