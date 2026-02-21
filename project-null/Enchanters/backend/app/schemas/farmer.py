from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.core.constants import LandUnit, IrrigationType, OwnershipType, DocType, Season


class FarmerCropCreate(BaseModel):
    crop_name: str = Field(..., min_length=1, max_length=100)
    season: Season
    year: int = Field(..., ge=2000, le=2100)


class FarmerCropResponse(BaseModel):
    id: UUID
    crop_name: str
    season: str
    year: int
    is_active: bool

    model_config = {"from_attributes": True}


class FarmerDocumentResponse(BaseModel):
    id: UUID
    doc_type: str
    file_key: str
    file_name: str
    uploaded_at: datetime
    verified: bool

    model_config = {"from_attributes": True}


class FarmerProfileCreate(BaseModel):
    aadhaar_masked: Optional[str] = Field(None, max_length=4, pattern=r"^\d{4}$")
    ration_card_no: Optional[str] = Field(None, max_length=20)
    bank_account: Optional[str] = Field(None, max_length=20)
    bank_ifsc: Optional[str] = Field(None, pattern=r"^[A-Z]{4}0[A-Z0-9]{6}$")
    irrigation_type: Optional[IrrigationType] = None
    ownership_type: Optional[OwnershipType] = None


class FarmerProfileResponse(BaseModel):
    aadhaar_masked: Optional[str] = None
    ration_card_no: Optional[str] = None
    bank_ifsc: Optional[str] = None
    irrigation_type: Optional[str] = None
    ownership_type: Optional[str] = None

    model_config = {"from_attributes": True}


class FarmerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    pin_code: Optional[str] = Field(None, pattern=r"^\d{6}$")
    land_area: Optional[float] = Field(None, gt=0)
    land_unit: Optional[LandUnit] = None
    language_pref: Optional[str] = None


class FarmerResponse(BaseModel):
    id: UUID
    farmer_id: str
    name: str
    phone: str
    email: Optional[str] = None
    email_verified: bool
    phone_verified: bool
    pin_code: str
    district: Optional[str] = None
    state: Optional[str] = None
    land_area: float
    land_unit: str
    language_pref: str
    created_at: datetime
    updated_at: datetime
    profile: Optional[FarmerProfileResponse] = None
    crops: List[FarmerCropResponse] = []
    documents: List[FarmerDocumentResponse] = []

    model_config = {"from_attributes": True}


class FarmerBrief(BaseModel):
    """Minimal farmer info returned to agents during lookup."""
    name: str
    phone_masked: str
    farmer_id: str
    district: Optional[str] = None
    state: Optional[str] = None


class AccessLogEntry(BaseModel):
    id: UUID
    agent_name: str
    center_name: Optional[str] = None
    purpose: Optional[str] = None
    session_start: Optional[datetime] = None
    session_end: Optional[datetime] = None
    status: str

    model_config = {"from_attributes": True}


class GeneratedFormResponse(BaseModel):
    id: UUID
    scheme_id: Optional[UUID] = None
    file_key: str
    file_name: str
    generated_at: datetime
    generated_by: str

    model_config = {"from_attributes": True}
