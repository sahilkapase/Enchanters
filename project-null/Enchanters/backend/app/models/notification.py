import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, ForeignKey, DateTime, Enum, Date,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.core.constants import ReminderType, ReminderChannel, GeneratedByType


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(ReminderType, name="reminder_type_enum"), nullable=False)
    reference_id = Column(UUID(as_uuid=True), nullable=False)
    remind_date = Column(Date, nullable=False)
    channel = Column(Enum(ReminderChannel, name="reminder_channel_enum"), nullable=False)
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True))

    farmer = relationship("Farmer", back_populates="reminders")


class GeneratedForm(Base):
    __tablename__ = "generated_forms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id", ondelete="SET NULL"), nullable=True)
    file_key = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    generated_by = Column(Enum(GeneratedByType, name="generated_by_type_enum"), nullable=False)
    agent_session_id = Column(UUID(as_uuid=True), ForeignKey("agent_sessions.id", ondelete="SET NULL"), nullable=True)

    farmer = relationship("Farmer", back_populates="generated_forms")
    scheme = relationship("Scheme")
    agent_session = relationship("AgentSession")
