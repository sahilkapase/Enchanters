from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_farmer
from app.schemas.auth import (
    SignupRequest, SignupResponse, VerifyOTPRequest, VerifyOTPResponse,
    LoginRequest, LoginResponse, LoginVerifyRequest, TokenResponse,
    RefreshRequest, MessageResponse,
)
from app.services import auth_service
from app.models.farmer import Farmer

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=SignupResponse)
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)):
    result = await auth_service.signup_farmer(
        db=db,
        name=body.name,
        phone=body.phone,
        pin_code=body.pin_code,
        land_area=body.land_area,
        land_unit=body.land_unit.value,
        email=body.email,
    )
    return result


@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(body: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    result = await auth_service.verify_farmer_otp(db, body.phone, body.otp, body.type)
    return result


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    result = await auth_service.login_farmer(body.phone)
    return result


@router.post("/login/verify", response_model=TokenResponse)
async def login_verify(body: LoginVerifyRequest, db: AsyncSession = Depends(get_db)):
    result = await auth_service.verify_login(db, body.phone, body.otp)
    return result


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest):
    result = await auth_service.refresh_tokens(body.refresh_token)
    return result


@router.post("/logout", response_model=MessageResponse)
async def logout(farmer: Farmer = Depends(get_current_farmer)):
    result = await auth_service.logout_farmer(str(farmer.id))
    return result
