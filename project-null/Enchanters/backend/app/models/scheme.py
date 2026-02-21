import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, ForeignKey, DateTime, Enum, Text, Date, Integer,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
from app.core.constants import BenefitType, RuleType


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_en = Column(String(300), nullable=False)
    name_hi = Column(String(300))
    ministry = Column(String(200))
    description_en = Column(Text)
    description_hi = Column(Text)
    benefit_type = Column(Enum(BenefitType, name="benefit_type_enum"), nullable=False)
    benefit_amount = Column(String(100))
    apply_url = Column(String(500))
    documents_required = Column(JSONB, default=list)
    how_to_apply = Column(Text)
    is_active = Column(Boolean, default=True)
    source_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    eligibility_rules = relationship("SchemeEligibility", back_populates="scheme", lazy="selectin")
    deadlines = relationship("SchemeDeadline", back_populates="scheme", lazy="selectin")


class SchemeEligibility(Base):
    __tablename__ = "scheme_eligibility"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False)
    rule_type = Column(Enum(RuleType, name="rule_type_enum"), nullable=False)
    rule_value = Column(String(200), nullable=False)
    is_mandatory = Column(Boolean, default=True)

    scheme = relationship("Scheme", back_populates="eligibility_rules")


class SchemeDeadline(Base):
    __tablename__ = "scheme_deadlines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False)
    season = Column(Enum("kharif", "rabi", "zaid", name="deadline_season_enum"))
    year = Column(Integer)
    open_date = Column(Date)
    close_date = Column(Date)
    state = Column(String(100))

    scheme = relationship("Scheme", back_populates="deadlines")
