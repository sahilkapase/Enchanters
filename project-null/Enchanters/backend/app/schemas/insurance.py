from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from app.core.constants import Season


class InsurancePlanResponse(BaseModel):
    id: UUID
    name_en: str
    name_hi: Optional[str] = None
    plan_type: str
    description_en: Optional[str] = None
    description_hi: Optional[str] = None
    coverage: Optional[str] = None
    premium_info: Optional[str] = None
    eligibility: Optional[str] = None
    how_to_enroll: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


class PremiumCalculateRequest(BaseModel):
    crop: str = Field(..., min_length=1, max_length=100)
    season: Season
    district: str = Field(..., min_length=1, max_length=100)
    land_area: float = Field(..., gt=0)


class PremiumCalculateResponse(BaseModel):
    crop: str
    season: str
    district: str
    land_area: float
    sum_insured: float
    farmer_premium: float
    govt_subsidy: float
    insurance_company: str
    premium_rate_percent: float
    source: str  # "pmfby_api" or "local_calculation"
