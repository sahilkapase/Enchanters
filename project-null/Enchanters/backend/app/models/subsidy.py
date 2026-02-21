import uuid
from sqlalchemy import Column, String, Boolean, Enum, Text, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base
from app.core.constants import SubsidyCategory


class Subsidy(Base):
    __tablename__ = "subsidies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_en = Column(String(300), nullable=False)
    name_hi = Column(String(300))
    category = Column(Enum(SubsidyCategory, name="subsidy_category_enum"), nullable=False)
    description_en = Column(Text)
    description_hi = Column(Text)
    benefit_amount = Column(String(100))
    eligibility = Column(JSONB, default=dict)
    open_date = Column(Date)
    close_date = Column(Date)
    state = Column(String(100))
    is_active = Column(Boolean, default=True)
