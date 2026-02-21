from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.farmer import Farmer, FarmerProfile, FarmerCrop, FarmerDocument
from app.models.agent import AgentSession
from app.models.notification import GeneratedForm
from app.core.security import encrypt_value, decrypt_value
from app.core.exceptions import NotFoundException, BadRequestException
from app.external.india_post import lookup_pincode
import logging

logger = logging.getLogger(__name__)


async def get_farmer_full(db: AsyncSession, farmer_uuid: UUID) -> Farmer:
    result = await db.execute(
        select(Farmer)
        .options(
            selectinload(Farmer.profile),
            selectinload(Farmer.crops),
            selectinload(Farmer.documents),
        )
        .where(Farmer.id == farmer_uuid)
    )
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise NotFoundException("Farmer")
    return farmer


async def update_farmer(db: AsyncSession, farmer_uuid: UUID, data: dict) -> Farmer:
    farmer = await get_farmer_full(db, farmer_uuid)

    if "pin_code" in data and data["pin_code"] and data["pin_code"] != farmer.pin_code:
        location = await lookup_pincode(data["pin_code"])
        data["district"] = location.get("district", farmer.district)
        data["state"] = location.get("state", farmer.state)

    for key, value in data.items():
        if value is not None and hasattr(farmer, key):
            setattr(farmer, key, value)

    await db.flush()
    await db.refresh(farmer)
    logger.info("Farmer updated: %s", farmer.farmer_id)
    return farmer


async def create_or_update_profile(db: AsyncSession, farmer_uuid: UUID, data: dict) -> FarmerProfile:
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.farmer_id == farmer_uuid)
    )
    profile = result.scalar_one_or_none()

    bank_account = data.pop("bank_account", None)
    aadhaar_masked = data.pop("aadhaar_masked", None)

    if profile:
        for key, value in data.items():
            if value is not None:
                setattr(profile, key, value)
        if bank_account is not None:
            profile.bank_account = encrypt_value(bank_account)
        if aadhaar_masked is not None:
            profile.aadhaar_masked = aadhaar_masked
    else:
        profile = FarmerProfile(farmer_id=farmer_uuid, **data)
        if bank_account:
            profile.bank_account = encrypt_value(bank_account)
        if aadhaar_masked:
            profile.aadhaar_masked = aadhaar_masked
        db.add(profile)

    await db.flush()
    await db.refresh(profile)
    logger.info("Profile updated for farmer_uuid=%s", farmer_uuid)
    return profile


async def list_crops(db: AsyncSession, farmer_uuid: UUID) -> list[FarmerCrop]:
    result = await db.execute(
        select(FarmerCrop)
        .where(FarmerCrop.farmer_id == farmer_uuid, FarmerCrop.is_active == True)
    )
    return list(result.scalars().all())


async def add_crop(db: AsyncSession, farmer_uuid: UUID, crop_name: str, season: str, year: int) -> FarmerCrop:
    crop = FarmerCrop(
        farmer_id=farmer_uuid,
        crop_name=crop_name.lower(),
        season=season,
        year=str(year),
    )
    db.add(crop)
    await db.flush()
    await db.refresh(crop)
    logger.info("Crop added: %s for farmer_uuid=%s", crop_name, farmer_uuid)
    return crop


async def remove_crop(db: AsyncSession, farmer_uuid: UUID, crop_id: UUID) -> dict:
    result = await db.execute(
        select(FarmerCrop).where(FarmerCrop.id == crop_id, FarmerCrop.farmer_id == farmer_uuid)
    )
    crop = result.scalar_one_or_none()
    if not crop:
        raise NotFoundException("Crop")
    crop.is_active = False
    await db.flush()
    return {"message": "Crop removed"}


async def list_documents(db: AsyncSession, farmer_uuid: UUID) -> list[FarmerDocument]:
    result = await db.execute(
        select(FarmerDocument).where(FarmerDocument.farmer_id == farmer_uuid)
    )
    return list(result.scalars().all())


async def delete_document(db: AsyncSession, farmer_uuid: UUID, doc_id: UUID) -> dict:
    result = await db.execute(
        select(FarmerDocument).where(FarmerDocument.id == doc_id, FarmerDocument.farmer_id == farmer_uuid)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundException("Document")
    await db.delete(doc)
    await db.flush()
    return {"message": "Document deleted"}


async def get_access_log(db: AsyncSession, farmer_uuid: UUID) -> list[dict]:
    from app.models.agent import Agent
    result = await db.execute(
        select(AgentSession, Agent.name, Agent.center_name)
        .join(Agent, AgentSession.agent_id == Agent.id)
        .where(AgentSession.farmer_id == farmer_uuid)
        .order_by(AgentSession.session_start.desc())
    )
    rows = result.all()
    return [
        {
            "id": session.id,
            "agent_name": agent_name,
            "center_name": center_name,
            "purpose": session.purpose,
            "session_start": session.session_start,
            "session_end": session.session_end,
            "status": session.status.value if session.status else "unknown",
        }
        for session, agent_name, center_name in rows
    ]


async def list_generated_forms(db: AsyncSession, farmer_uuid: UUID) -> list[GeneratedForm]:
    result = await db.execute(
        select(GeneratedForm)
        .where(GeneratedForm.farmer_id == farmer_uuid)
        .order_by(GeneratedForm.generated_at.desc())
    )
    return list(result.scalars().all())
