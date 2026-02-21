from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_farmer
from app.schemas.insurance import (
    InsurancePlanResponse, PremiumCalculateRequest, PremiumCalculateResponse,
)
from app.schemas.scheme import FormGenerateResponse
from app.services import insurance_service
from app.models.farmer import Farmer

router = APIRouter(prefix="/insurance", tags=["Insurance"])


@router.get("/plans", response_model=list[InsurancePlanResponse])
async def list_plans(
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await insurance_service.list_plans(db)


@router.get("/plans/{plan_id}", response_model=InsurancePlanResponse)
async def get_plan(
    plan_id: UUID,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await insurance_service.get_plan(db, plan_id)


@router.post("/calculate-premium", response_model=PremiumCalculateResponse)
async def calculate_premium(
    body: PremiumCalculateRequest,
    farmer: Farmer = Depends(get_current_farmer),
):
    return await insurance_service.calculate_premium(
        crop=body.crop,
        season=body.season.value,
        district=body.district,
        land_area=body.land_area,
    )


@router.post("/plans/{plan_id}/generate-form", response_model=FormGenerateResponse)
async def generate_insurance_form(
    plan_id: UUID,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await insurance_service.generate_insurance_form(db, plan_id, farmer, generated_by="farmer")
