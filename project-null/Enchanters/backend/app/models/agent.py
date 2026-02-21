import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, ForeignKey, DateTime, Enum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
from app.core.constants import CenterType, AgentSessionStatus


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False, unique=True)
    email = Column(String(255))
    center_name = Column(String(200))
    center_type = Column(Enum(CenterType, name="center_type_enum"))
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sessions = relationship("AgentSession", back_populates="agent", lazy="selectin")


class AgentSession(Base):
    __tablename__ = "agent_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    purpose = Column(String(300))
    otp_verified_at = Column(DateTime(timezone=True))
    session_start = Column(DateTime(timezone=True))
    session_end = Column(DateTime(timezone=True))
    forms_downloaded = Column(JSONB, default=list)
    actions_taken = Column(JSONB, default=list)
    status = Column(
        Enum(AgentSessionStatus, name="agent_session_status_enum"),
        default=AgentSessionStatus.ACTIVE,
    )

    agent = relationship("Agent", back_populates="sessions")
    farmer = relationship("Farmer")
