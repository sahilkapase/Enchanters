from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date
from app.core.constants import SubsidyCategory, ReminderChannel


class SubsidyListItem(BaseModel):
    id: UUID
    name_en: str
    name_hi: Optional[str] = None
    category: str
    benefit_amount: Optional[str] = None
    open_date: Optional[date] = None
    close_date: Optional[date] = None
    state: Optional[str] = None
    is_active: bool
    status: str  # "open", "closed", "upcoming"

    model_config = {"from_attributes": True}


class SubsidyDetail(BaseModel):
    id: UUID
    name_en: str
    name_hi: Optional[str] = None
    category: str
    description_en: Optional[str] = None
    description_hi: Optional[str] = None
    benefit_amount: Optional[str] = None
    eligibility: Optional[dict] = None
    open_date: Optional[date] = None
    close_date: Optional[date] = None
    state: Optional[str] = None
    is_active: bool
    status: str

    model_config = {"from_attributes": True}


class SubsidyCalendarItem(BaseModel):
    id: UUID
    name_en: str
    category: str
    open_date: Optional[date] = None
    close_date: Optional[date] = None
    state: Optional[str] = None
    status: str


class SubsidyRemindRequest(BaseModel):
    channel: ReminderChannel
