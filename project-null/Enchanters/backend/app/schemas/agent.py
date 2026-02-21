from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class AgentLoginRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    password: str = Field(..., min_length=6)


class AgentTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    agent_name: str
    center_name: Optional[str] = None


class FarmerLookupRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=50)


class FarmerLookupResponse(BaseModel):
    name: str
    phone_masked: str
    farmer_id: str
    district: Optional[str] = None
    state: Optional[str] = None


class RequestAccessRequest(BaseModel):
    farmer_identifier: str = Field(..., min_length=2)
    purpose: str = Field(..., min_length=5, max_length=300)


class RequestAccessResponse(BaseModel):
    session_id: UUID
    otp_sent: bool
    message: str


class VerifyAccessRequest(BaseModel):
    session_id: UUID
    otp: str = Field(..., pattern=r"^\d{6}$")


class VerifyAccessResponse(BaseModel):
    session_id: UUID
    farmer_id: str
    farmer_name: str
    expires_at: datetime
    message: str


class AgentSessionDetail(BaseModel):
    id: UUID
    agent_id: UUID
    farmer_id: UUID
    farmer_name: Optional[str] = None
    purpose: Optional[str] = None
    otp_verified_at: Optional[datetime] = None
    session_start: Optional[datetime] = None
    session_end: Optional[datetime] = None
    forms_downloaded: Optional[list] = []
    actions_taken: Optional[list] = []
    status: str
    time_remaining_seconds: Optional[int] = None

    model_config = {"from_attributes": True}


class AgentActivityItem(BaseModel):
    id: UUID
    farmer_id: str
    farmer_name: str
    purpose: Optional[str] = None
    session_start: Optional[datetime] = None
    session_end: Optional[datetime] = None
    status: str
    forms_count: int = 0
