from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.insurance import InsurancePlan
from app.models.farmer import Farmer
from app.models.notification import GeneratedForm
from app.core.constants import LandUnit, LAND_CONVERSION, GeneratedByType
from app.core.exceptions import NotFoundException
from app.core.pdf_builder import build_insurance_form_pdf
from app.external.pmfby import calculate_premium_from_api, calculate_premium_local
from app.services.document_service import upload_bytes_to_s3
import logging

logger = logging.getLogger(__name__)


async def list_plans(db: AsyncSession) -> list[InsurancePlan]:
    result = await db.execute(
        select(InsurancePlan).where(InsurancePlan.is_active == True)
    )
    return list(result.scalars().all())


async def get_plan(db: AsyncSession, plan_id: UUID) -> InsurancePlan:
    result = await db.execute(
        select(InsurancePlan).where(InsurancePlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundException("Insurance Plan")
    return plan


async def calculate_premium(
    crop: str,
    season: str,
    district: str,
    land_area: float,
    land_unit: str = "acre",
) -> dict:
    unit_enum = LandUnit(land_unit) if land_unit else LandUnit.ACRE
    factor = LAND_CONVERSION.get(unit_enum, 1.0)
    land_area_acres = land_area * factor
    land_area_hectares = land_area_acres / 2.47105

    api_result = await calculate_premium_from_api(crop, season, district, land_area_hectares)
    if api_result:
        return {
            "crop": crop,
            "season": season,
            "district": district,
            "land_area": land_area,
            **api_result,
        }

    local_result = calculate_premium_local(crop, season, district, land_area_hectares)
    return {
        "crop": crop,
        "season": season,
        "district": district,
        "land_area": land_area,
        **local_result,
    }


async def generate_insurance_form(
    db: AsyncSession,
    plan_id: UUID,
    farmer: Farmer,
    generated_by: str = "farmer",
    agent_session_id: UUID | None = None,
) -> dict:
    plan = await get_plan(db, plan_id)

    farmer_data = {
        "farmer_id": farmer.farmer_id,
        "name": farmer.name,
        "phone": farmer.phone,
        "district": farmer.district,
        "state": farmer.state,
        "pin_code": farmer.pin_code,
        "land_area": str(farmer.land_area),
        "land_unit": farmer.land_unit.value if hasattr(farmer.land_unit, 'value') else str(farmer.land_unit),
    }
    plan_data = {
        "name_en": plan.name_en,
        "plan_type": plan.plan_type.value if hasattr(plan.plan_type, 'value') else str(plan.plan_type),
    }

    pdf_bytes, filename = build_insurance_form_pdf(farmer_data, plan_data)
    file_key = f"forms/{farmer.farmer_id}/insurance/{plan_id}/{filename}"
    await upload_bytes_to_s3(pdf_bytes, file_key, "application/pdf")

    form = GeneratedForm(
        farmer_id=farmer.id,
        scheme_id=None,
        file_key=file_key,
        file_name=filename,
        generated_by=GeneratedByType(generated_by),
        agent_session_id=agent_session_id,
    )
    db.add(form)
    await db.flush()

    logger.info("Insurance form generated: %s", filename)
    return {
        "file_key": file_key,
        "file_name": filename,
        "download_url": f"/files/{file_key}",
        "message": "Insurance form generated successfully",
    }
