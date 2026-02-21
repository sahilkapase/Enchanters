from pydantic import BaseModel, Field
from typing import Optional
from app.core.constants import LandUnit


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    email: Optional[str] = None
    pin_code: str = Field(..., pattern=r"^\d{6}$")
    land_area: float = Field(..., gt=0)
    land_unit: LandUnit = LandUnit.ACRE


class SignupResponse(BaseModel):
    message: str
    farmer_id: str


class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    otp: str = Field(..., pattern=r"^\d{6}$")
    type: str = Field(default="phone", pattern=r"^(phone|email)$")


class VerifyOTPResponse(BaseModel):
    verified: bool


class LoginRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")


class LoginResponse(BaseModel):
    message: str


class LoginVerifyRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    otp: str = Field(..., pattern=r"^\d{6}$")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    farmer_id: str


class RefreshRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    message: str
