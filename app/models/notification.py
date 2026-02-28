import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class NotificationType(Base):
    __tablename__ = "notification_type"

    notification_type_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    notification_type_name: Mapped[str] = mapped_column(String(255), nullable=False)

    notifications: Mapped[list["LeadNotification"]] = relationship(
        "LeadNotification", back_populates="notification_type"
    )


class LeadNotification(Base):
    __tablename__ = "lead_notification"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    lead_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("lead.id"), nullable=False, index=True
    )
    notification_type_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("notification_type.notification_type_id"),
        nullable=False,
        default="email_new_lead_submission",
    )
    is_lead_notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_attorney_notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attorney_notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    lead_notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    lead: Mapped["Lead"] = relationship("Lead", back_populates="notifications")  # noqa: F821
    notification_type: Mapped["NotificationType"] = relationship(
        "NotificationType", back_populates="notifications"
    )
