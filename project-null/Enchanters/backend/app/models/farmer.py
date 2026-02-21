import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Numeric, ForeignKey, DateTime, Enum, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.core.constants import LandUnit, IrrigationType, OwnershipType, DocType


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(String(11), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    pin_code = Column(String(6), nullable=False)
    district = Column(String(100))
    state = Column(String(100))
    land_area = Column(Numeric(10, 2), nullable=False)
    land_unit = Column(Enum(LandUnit, name="land_unit_enum"), default=LandUnit.ACRE)
    language_pref = Column(String(10), default="hi")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    profile = relationship("FarmerProfile", back_populates="farmer", uselist=False, lazy="selectin")
    crops = relationship("FarmerCrop", back_populates="farmer", lazy="selectin")
    documents = relationship("FarmerDocument", back_populates="farmer", lazy="selectin")
    reminders = relationship("Reminder", back_populates="farmer", lazy="selectin")
    generated_forms = relationship("GeneratedForm", back_populates="farmer", lazy="selectin")


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), unique=True, nullable=False)
    aadhaar_masked = Column(String(8))
    ration_card_no = Column(String(20))
    bank_account = Column(String(255))  # encrypted at rest
    bank_ifsc = Column(String(11))
    irrigation_type = Column(Enum(IrrigationType, name="irrigation_type_enum"))
    ownership_type = Column(Enum(OwnershipType, name="ownership_type_enum"))

    farmer = relationship("Farmer", back_populates="profile")


class FarmerCrop(Base):
    __tablename__ = "farmer_crops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    crop_name = Column(String(100), nullable=False)
    season = Column(Enum("kharif", "rabi", "zaid", name="season_enum"), nullable=False)
    year = Column(String(4), nullable=False)
    is_active = Column(Boolean, default=True)

    farmer = relationship("Farmer", back_populates="crops")


class FarmerDocument(Base):
    __tablename__ = "farmer_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    doc_type = Column(Enum(DocType, name="doc_type_enum"), nullable=False)
    file_key = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    verified = Column(Boolean, default=False)

    farmer = relationship("Farmer", back_populates="documents")
