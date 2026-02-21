from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.farmer import Farmer
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.otp import send_and_store_otp, verify_otp, store_refresh_token, is_refresh_token_valid, revoke_refresh_token
from app.core.id_generator import generate_farmer_id
from app.core.exceptions import (
    BadRequestException, NotFoundException, UnauthorizedException, ConflictException,
)
from app.external.india_post import lookup_pincode
from app.external.sms import send_otp_sms
from app.external.email import send_otp_email
import logging

logger = logging.getLogger(__name__)


async def signup_farmer(
    db: AsyncSession,
    name: str,
    phone: str,
    pin_code: str,
    land_area: float,
    land_unit: str,
    email: str | None = None,
) -> dict:
    existing = await db.execute(select(Farmer).where(Farmer.phone == phone))
    if existing.scalar_one_or_none():
        raise ConflictException("A farmer with this phone number already exists")

    location = await lookup_pincode(pin_code)
    district = location.get("district", "")
    state = location.get("state", "")

    farmer_id = await generate_farmer_id(db)

    farmer = Farmer(
        farmer_id=farmer_id,
        name=name,
        phone=phone,
        email=email,
        pin_code=pin_code,
        district=district,
        state=state,
        land_area=land_area,
        land_unit=land_unit,
        phone_verified=False,
        email_verified=False,
    )
    db.add(farmer)
    await db.flush()

    otp = await send_and_store_otp(phone, "phone")
    await send_otp_sms(phone, otp)

    if email:
        email_otp = await send_and_store_otp(phone, "email")
        await send_otp_email(email, email_otp)

    logger.info("Farmer signed up: %s (farmer_id=%s)", phone[-4:], farmer_id)
    return {"message": "Signup successful. OTP sent to your phone.", "farmer_id": farmer_id}


async def verify_farmer_otp(db: AsyncSession, phone: str, otp: str, otp_type: str = "phone") -> dict:
    farmer_result = await db.execute(select(Farmer).where(Farmer.phone == phone))
    farmer = farmer_result.scalar_one_or_none()
    if not farmer:
        raise NotFoundException("Farmer")

    await verify_otp(phone, otp, otp_type)

    if otp_type == "phone":
        farmer.phone_verified = True
    elif otp_type == "email":
        farmer.email_verified = True

    await db.flush()
    logger.info("OTP verified for farmer %s (type=%s)", farmer.farmer_id, otp_type)
    return {"verified": True}


async def login_farmer(phone: str) -> dict:
    otp = await send_and_store_otp(phone, "login")
    await send_otp_sms(phone, otp)
    logger.info("Login OTP sent to %s***%s", phone[:2], phone[-2:])
    return {"message": "OTP sent to your phone"}


async def verify_login(db: AsyncSession, phone: str, otp: str) -> dict:
    farmer_result = await db.execute(select(Farmer).where(Farmer.phone == phone))
    farmer = farmer_result.scalar_one_or_none()
    if not farmer:
        raise NotFoundException("Farmer")

    await verify_otp(phone, otp, "login")

    if not farmer.phone_verified:
        farmer.phone_verified = True
        await db.flush()

    access_token = create_access_token(str(farmer.id), extra_claims={"farmer_id": farmer.farmer_id, "role": "farmer"})
    refresh_token = create_refresh_token(str(farmer.id))

    await store_refresh_token(str(farmer.id), refresh_token)

    logger.info("Farmer logged in: %s", farmer.farmer_id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "farmer_id": farmer.farmer_id,
    }


async def refresh_tokens(refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedException("Invalid refresh token")

    subject = payload["sub"]
    if not await is_refresh_token_valid(subject, refresh_token):
        raise UnauthorizedException("Refresh token has been revoked")

    new_access = create_access_token(subject, extra_claims={"role": "farmer"})
    new_refresh = create_refresh_token(subject)
    await store_refresh_token(subject, new_refresh)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "farmer_id": "",
    }


async def logout_farmer(farmer_id: str) -> dict:
    await revoke_refresh_token(farmer_id)
    return {"message": "Logged out successfully"}
