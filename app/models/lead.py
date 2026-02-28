import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, LargeBinary, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class LeadState(Base):
    __tablename__ = "lead_state"

    lead_state_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    lead_state_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    leads: Mapped[list["Lead"]] = relationship("Lead", back_populates="state")


class Lead(Base):
    __tablename__ = "lead"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    resume: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    resume_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    lead_state_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("lead_state.lead_state_id"), nullable=False, default="PENDING"
    )
    handled_by_user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("user.id"), nullable=True
    )
    attorney_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    state: Mapped["LeadState"] = relationship("LeadState", back_populates="leads")
    handler: Mapped["User | None"] = relationship("User", back_populates="handled_leads")
    notifications: Mapped[list["LeadNotification"]] = relationship(  # noqa: F821
        "LeadNotification", back_populates="lead"
    )
