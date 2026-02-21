from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, extract
from app.models.subsidy import Subsidy
from app.models.farmer import Farmer
from app.models.notification import Reminder
from app.core.constants import ReminderType
from app.core.exceptions import NotFoundException, BadRequestException
import logging

logger = logging.getLogger(__name__)


def _get_subsidy_status(s: Subsidy) -> str:
    today = date.today()
    if s.open_date and s.close_date:
        if today < s.open_date:
            return "upcoming"
        elif today > s.close_date:
            return "closed"
        else:
            return "open"
    elif s.open_date and not s.close_date:
        return "open" if today >= s.open_date else "upcoming"
    return "open" if s.is_active else "closed"


async def list_subsidies(
    db: AsyncSession,
    category: str | None = None,
    state: str | None = None,
    status_filter: str | None = None,
) -> list[dict]:
    query = select(Subsidy).where(Subsidy.is_active == True)

    if category:
        query = query.where(Subsidy.category == category)
    if state:
        query = query.where(
            or_(Subsidy.state == state, Subsidy.state.is_(None), Subsidy.state == "")
        )

    result = await db.execute(query)
    subsidies = result.scalars().all()

    items = []
    for s in subsidies:
        st = _get_subsidy_status(s)
        if status_filter and st != status_filter:
            continue
        items.append({
            "id": s.id,
            "name_en": s.name_en,
            "name_hi": s.name_hi,
            "category": s.category.value if hasattr(s.category, 'value') else str(s.category),
            "benefit_amount": s.benefit_amount,
            "open_date": s.open_date,
            "close_date": s.close_date,
            "state": s.state,
            "is_active": s.is_active,
            "status": st,
        })

    return items


async def get_subsidy(db: AsyncSession, subsidy_id: UUID) -> dict:
    result = await db.execute(
        select(Subsidy).where(Subsidy.id == subsidy_id)
    )
    s = result.scalar_one_or_none()
    if not s:
        raise NotFoundException("Subsidy")

    return {
        "id": s.id,
        "name_en": s.name_en,
        "name_hi": s.name_hi,
        "category": s.category.value if hasattr(s.category, 'value') else str(s.category),
        "description_en": s.description_en,
        "description_hi": s.description_hi,
        "benefit_amount": s.benefit_amount,
        "eligibility": s.eligibility,
        "open_date": s.open_date,
        "close_date": s.close_date,
        "state": s.state,
        "is_active": s.is_active,
        "status": _get_subsidy_status(s),
    }


async def get_calendar(db: AsyncSession, month: int, year: int) -> list[dict]:
    result = await db.execute(
        select(Subsidy).where(
            Subsidy.is_active == True,
            or_(
                and_(
                    extract("month", Subsidy.open_date) == month,
                    extract("year", Subsidy.open_date) == year,
                ),
                and_(
                    extract("month", Subsidy.close_date) == month,
                    extract("year", Subsidy.close_date) == year,
                ),
                and_(
                    Subsidy.open_date <= date(year, month, 1),
                    Subsidy.close_date >= date(year, month, 1),
                ),
            ),
        )
    )
    subsidies = result.scalars().all()

    return [
        {
            "id": s.id,
            "name_en": s.name_en,
            "category": s.category.value if hasattr(s.category, 'value') else str(s.category),
            "open_date": s.open_date,
            "close_date": s.close_date,
            "state": s.state,
            "status": _get_subsidy_status(s),
        }
        for s in subsidies
    ]


async def create_subsidy_reminder(
    db: AsyncSession,
    subsidy_id: UUID,
    farmer: Farmer,
    channel: str,
) -> dict:
    result = await db.execute(
        select(Subsidy).where(Subsidy.id == subsidy_id)
    )
    s = result.scalar_one_or_none()
    if not s:
        raise NotFoundException("Subsidy")

    today = date.today()
    if s.close_date and s.close_date <= today:
        raise BadRequestException("This subsidy has already closed")

    from datetime import timedelta
    if s.close_date:
        remind_date = s.close_date - timedelta(days=3)
        if remind_date < today:
            remind_date = today
    elif s.open_date and s.open_date > today:
        remind_date = s.open_date
    else:
        remind_date = today

    reminder = Reminder(
        farmer_id=farmer.id,
        type=ReminderType.SUBSIDY,
        reference_id=s.id,
        remind_date=remind_date,
        channel=channel,
    )
    db.add(reminder)
    await db.flush()

    return {"message": f"Reminder set for {remind_date.isoformat()} via {channel}"}
