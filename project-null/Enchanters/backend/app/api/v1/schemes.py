from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_farmer
from app.schemas.scheme import (
    SchemeListItem, SchemeDetail, EligibilityBreakdown,
    SchemeRemindRequest, FormGenerateResponse,
)
from app.services import scheme_service
from app.models.farmer import Farmer

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get("", response_model=list[SchemeListItem])
async def list_schemes(
    crop: str | None = Query(None),
    season: str | None = Query(None),
    state: str | None = Query(None),
    land_area: float | None = Query(None),
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    results = await scheme_service.list_schemes_with_eligibility(
        db, farmer, crop=crop, season=season, state=state, land_area=land_area
    )
    return results


@router.get("/{scheme_id}", response_model=SchemeDetail)
async def get_scheme(
    scheme_id: UUID,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await scheme_service.get_scheme_detail(db, scheme_id, farmer)


@router.get("/{scheme_id}/eligibility", response_model=EligibilityBreakdown)
async def check_eligibility(
    scheme_id: UUID,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await scheme_service.get_eligibility_breakdown(db, scheme_id, farmer)


@router.post("/{scheme_id}/generate-form", response_model=FormGenerateResponse)
async def generate_form(
    scheme_id: UUID,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await scheme_service.generate_scheme_form(db, scheme_id, farmer, generated_by="farmer")


@router.post("/{scheme_id}/remind")
async def set_reminder(
    scheme_id: UUID,
    body: SchemeRemindRequest,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await scheme_service.create_scheme_reminder(
        db, scheme_id, farmer, body.channel.value
    )
