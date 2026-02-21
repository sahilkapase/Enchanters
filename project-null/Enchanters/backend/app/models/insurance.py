import uuid
from sqlalchemy import Column, String, Boolean, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.core.constants import InsurancePlanType


class InsurancePlan(Base):
    __tablename__ = "insurance_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_en = Column(String(300), nullable=False)
    name_hi = Column(String(300))
    plan_type = Column(Enum(InsurancePlanType, name="insurance_plan_type_enum"), nullable=False)
    description_en = Column(Text)
    description_hi = Column(Text)
    coverage = Column(Text)
    premium_info = Column(Text)
    eligibility = Column(Text)
    how_to_enroll = Column(Text)
    is_active = Column(Boolean, default=True)
