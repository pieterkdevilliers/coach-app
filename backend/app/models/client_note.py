import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ClientNote(Base):
    __tablename__ = "client_notes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id"), nullable=False, index=True
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("businesses.id"), nullable=False, index=True
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
