from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_farmer
from app.schemas.subsidy import (
    SubsidyListItem, SubsidyDetail, SubsidyCalendarItem, SubsidyRemindRequest,
)
from app.services import subsidy_service
from app.models.farmer import Farmer

router = APIRouter(prefix="/subsidies", tags=["Subsidies"])


@router.get("", response_model=list[SubsidyListItem])
async def list_subsidies(
    category: str | None = Query(None),
    state: str | None = Query(None),
    status: str | None = Query(None),
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await subsidy_service.list_subsidies(db, category=category, state=state, status_filter=status)


@router.get("/calendar", response_model=list[SubsidyCalendarItem])
async def calendar(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await subsidy_service.get_calendar(db, month, year)


@router.get("/{subsidy_id}", response_model=SubsidyDetail)
async def get_subsidy(
    subsidy_id: UUID,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await subsidy_service.get_subsidy(db, subsidy_id)


@router.post("/{subsidy_id}/remind")
async def set_reminder(
    subsidy_id: UUID,
    body: SubsidyRemindRequest,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await subsidy_service.create_subsidy_reminder(
        db, subsidy_id, farmer, body.channel.value
    )
