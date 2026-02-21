from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from app.core.constants import BenefitType, ReminderChannel, EligibilityStatus


class SchemeEligibilityRule(BaseModel):
    rule_type: str
    rule_value: str
    is_mandatory: bool

    model_config = {"from_attributes": True}


class SchemeDeadlineResponse(BaseModel):
    id: UUID
    season: Optional[str] = None
    year: Optional[int] = None
    open_date: Optional[date] = None
    close_date: Optional[date] = None
    state: Optional[str] = None

    model_config = {"from_attributes": True}


class SchemeListItem(BaseModel):
    id: UUID
    name_en: str
    name_hi: Optional[str] = None
    ministry: Optional[str] = None
    benefit_type: str
    benefit_amount: Optional[str] = None
    is_active: bool
    eligibility_status: Optional[EligibilityStatus] = None
    match_score: Optional[float] = None
    matched_rules: List[str] = []
    unmatched_rules: List[str] = []

    model_config = {"from_attributes": True}


class SchemeDetail(BaseModel):
    id: UUID
    name_en: str
    name_hi: Optional[str] = None
    ministry: Optional[str] = None
    description_en: Optional[str] = None
    description_hi: Optional[str] = None
    benefit_type: str
    benefit_amount: Optional[str] = None
    apply_url: Optional[str] = None
    documents_required: List[str] = []
    how_to_apply: Optional[str] = None
    is_active: bool
    source_url: Optional[str] = None
    eligibility_rules: List[SchemeEligibilityRule] = []
    deadlines: List[SchemeDeadlineResponse] = []
    eligibility_status: Optional[EligibilityStatus] = None
    match_score: Optional[float] = None
    matched_rules: List[str] = []
    unmatched_rules: List[str] = []

    model_config = {"from_attributes": True}


class EligibilityBreakdown(BaseModel):
    scheme_id: UUID
    scheme_name: str
    status: EligibilityStatus
    score: float
    total_rules: int
    mandatory_rules: int
    matched_mandatory: int
    matched_rules: List[dict]
    unmatched_rules: List[dict]


class SchemeRemindRequest(BaseModel):
    channel: ReminderChannel


class FormGenerateResponse(BaseModel):
    file_key: str
    file_name: str
    download_url: Optional[str] = None
    message: str
