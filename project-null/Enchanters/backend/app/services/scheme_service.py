"""
Scheme Eligibility Engine — the core business logic of KisaanSeva.

For each active scheme, evaluates the farmer's data against every eligibility rule
and produces a match score, status, and detailed breakdown.
"""

from uuid import UUID
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.scheme import Scheme, SchemeEligibility, SchemeDeadline
from app.models.farmer import Farmer, FarmerProfile, FarmerCrop
from app.models.notification import Reminder, GeneratedForm
from app.core.constants import (
    RuleType, LandUnit, LAND_CONVERSION, EligibilityStatus,
    ReminderType, GeneratedByType,
)
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.pdf_builder import build_scheme_form_pdf
from app.services.document_service import upload_bytes_to_s3
import logging

logger = logging.getLogger(__name__)


def _normalize_land_to_acres(area: float | Decimal, unit: str) -> float:
    """Convert any land unit to acres for comparison."""
    unit_enum = LandUnit(unit) if isinstance(unit, str) else unit
    factor = LAND_CONVERSION.get(unit_enum, 1.0)
    return float(area) * factor


def _check_rule(rule: SchemeEligibility, farmer_data: dict) -> bool:
    """Check whether a single eligibility rule is satisfied by the farmer's data."""
    rt = rule.rule_type
    rv = rule.rule_value.strip().lower()

    if rt == RuleType.CROP:
        farmer_crops = [c.lower() for c in farmer_data.get("crops", [])]
        return rv in farmer_crops

    elif rt == RuleType.LAND_MIN:
        try:
            threshold = float(rv.replace(">=", "").replace("<=", "").strip())
        except ValueError:
            return False
        return farmer_data.get("land_area_acres", 0) >= threshold

    elif rt == RuleType.LAND_MAX:
        try:
            threshold = float(rv.replace(">=", "").replace("<=", "").strip())
        except ValueError:
            return False
        return farmer_data.get("land_area_acres", 0) <= threshold

    elif rt == RuleType.STATE:
        return farmer_data.get("state", "").lower() == rv

    elif rt == RuleType.DISTRICT:
        return farmer_data.get("district", "").lower() == rv

    elif rt == RuleType.SEASON:
        farmer_seasons = [s.lower() for s in farmer_data.get("seasons", [])]
        return rv in farmer_seasons

    elif rt == RuleType.OWNERSHIP:
        return farmer_data.get("ownership_type", "").lower() == rv

    elif rt == RuleType.IRRIGATION:
        return farmer_data.get("irrigation_type", "").lower() == rv

    return False


def evaluate_eligibility(scheme: Scheme, farmer_data: dict) -> dict:
    """
    Evaluate a scheme against farmer data.
    Returns: {status, score, matched_rules, unmatched_rules, total_rules, mandatory_rules, matched_mandatory}
    """
    rules = scheme.eligibility_rules
    if not rules:
        return {
            "status": EligibilityStatus.ELIGIBLE,
            "score": 1.0,
            "matched_rules": [],
            "unmatched_rules": [],
            "total_rules": 0,
            "mandatory_rules": 0,
            "matched_mandatory": 0,
        }

    matched = []
    unmatched = []
    mandatory_total = 0
    mandatory_matched = 0

    for rule in rules:
        passed = _check_rule(rule, farmer_data)
        rule_info = {
            "rule_type": rule.rule_type.value if hasattr(rule.rule_type, 'value') else str(rule.rule_type),
            "rule_value": rule.rule_value,
            "is_mandatory": rule.is_mandatory,
            "passed": passed,
        }

        if passed:
            matched.append(rule_info)
            if rule.is_mandatory:
                mandatory_matched += 1
        else:
            unmatched.append(rule_info)

        if rule.is_mandatory:
            mandatory_total += 1

    if mandatory_total == 0:
        score = 1.0
    else:
        score = mandatory_matched / mandatory_total

    if mandatory_total == 0 or mandatory_matched == mandatory_total:
        status = EligibilityStatus.ELIGIBLE
    elif mandatory_matched > 0:
        status = EligibilityStatus.PARTIAL
    else:
        status = EligibilityStatus.NOT_ELIGIBLE

    return {
        "status": status,
        "score": round(score, 3),
        "matched_rules": matched,
        "unmatched_rules": unmatched,
        "total_rules": len(rules),
        "mandatory_rules": mandatory_total,
        "matched_mandatory": mandatory_matched,
    }


def _build_farmer_data(farmer: Farmer) -> dict:
    """Extract structured data from a Farmer ORM instance for eligibility checking."""
    profile = farmer.profile
    crops = farmer.crops or []
    crop_names = [c.crop_name.lower() for c in crops if c.is_active]
    seasons = list({c.season for c in crops if c.is_active})

    land_area_acres = _normalize_land_to_acres(
        farmer.land_area,
        farmer.land_unit.value if hasattr(farmer.land_unit, 'value') else str(farmer.land_unit),
    )

    data = {
        "crops": crop_names,
        "seasons": seasons,
        "state": (farmer.state or "").strip(),
        "district": (farmer.district or "").strip(),
        "land_area_acres": land_area_acres,
        "ownership_type": "",
        "irrigation_type": "",
    }

    if profile:
        if profile.ownership_type:
            data["ownership_type"] = profile.ownership_type.value if hasattr(profile.ownership_type, 'value') else str(profile.ownership_type)
        if profile.irrigation_type:
            data["irrigation_type"] = profile.irrigation_type.value if hasattr(profile.irrigation_type, 'value') else str(profile.irrigation_type)

    return data


async def list_schemes_with_eligibility(
    db: AsyncSession,
    farmer: Farmer,
    crop: str | None = None,
    season: str | None = None,
    state: str | None = None,
    land_area: float | None = None,
) -> list[dict]:
    """List all active schemes with eligibility check for the given farmer."""
    result = await db.execute(
        select(Scheme)
        .options(selectinload(Scheme.eligibility_rules), selectinload(Scheme.deadlines))
        .where(Scheme.is_active == True)
    )
    schemes = result.scalars().all()

    farmer_data = _build_farmer_data(farmer)

    if crop:
        farmer_data["crops"] = list(set(farmer_data["crops"] + [crop.lower()]))
    if season:
        farmer_data["seasons"] = list(set(farmer_data["seasons"] + [season.lower()]))
    if state:
        farmer_data["state"] = state
    if land_area is not None:
        farmer_data["land_area_acres"] = land_area

    results = []
    today = date.today()

    for scheme in schemes:
        elig = evaluate_eligibility(scheme, farmer_data)

        nearest_deadline = None
        for dl in (scheme.deadlines or []):
            if dl.close_date and dl.close_date >= today:
                if nearest_deadline is None or dl.close_date < nearest_deadline:
                    nearest_deadline = dl.close_date

        results.append({
            "id": scheme.id,
            "name_en": scheme.name_en,
            "name_hi": scheme.name_hi,
            "ministry": scheme.ministry,
            "benefit_type": scheme.benefit_type.value if hasattr(scheme.benefit_type, 'value') else str(scheme.benefit_type),
            "benefit_amount": scheme.benefit_amount,
            "is_active": scheme.is_active,
            "eligibility_status": elig["status"],
            "match_score": elig["score"],
            "matched_rules": [f"{r['rule_type']}={r['rule_value']}" for r in elig["matched_rules"]],
            "unmatched_rules": [f"{r['rule_type']}={r['rule_value']}" for r in elig["unmatched_rules"]],
            "_deadline_proximity": nearest_deadline,
        })

    results.sort(key=lambda x: (
        -x["match_score"],
        x["_deadline_proximity"] or date(9999, 12, 31),
    ))

    for r in results:
        r.pop("_deadline_proximity", None)

    return results


async def get_scheme_detail(db: AsyncSession, scheme_id: UUID, farmer: Farmer) -> dict:
    result = await db.execute(
        select(Scheme)
        .options(selectinload(Scheme.eligibility_rules), selectinload(Scheme.deadlines))
        .where(Scheme.id == scheme_id)
    )
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise NotFoundException("Scheme")

    farmer_data = _build_farmer_data(farmer)
    elig = evaluate_eligibility(scheme, farmer_data)

    return {
        "id": scheme.id,
        "name_en": scheme.name_en,
        "name_hi": scheme.name_hi,
        "ministry": scheme.ministry,
        "description_en": scheme.description_en,
        "description_hi": scheme.description_hi,
        "benefit_type": scheme.benefit_type.value if hasattr(scheme.benefit_type, 'value') else str(scheme.benefit_type),
        "benefit_amount": scheme.benefit_amount,
        "apply_url": scheme.apply_url,
        "documents_required": scheme.documents_required or [],
        "how_to_apply": scheme.how_to_apply,
        "is_active": scheme.is_active,
        "source_url": scheme.source_url,
        "eligibility_rules": [
            {
                "rule_type": r.rule_type.value if hasattr(r.rule_type, 'value') else str(r.rule_type),
                "rule_value": r.rule_value,
                "is_mandatory": r.is_mandatory,
            }
            for r in scheme.eligibility_rules
        ],
        "deadlines": [
            {
                "id": d.id,
                "season": d.season,
                "year": d.year,
                "open_date": d.open_date,
                "close_date": d.close_date,
                "state": d.state,
            }
            for d in scheme.deadlines
        ],
        "eligibility_status": elig["status"],
        "match_score": elig["score"],
        "matched_rules": [f"{r['rule_type']}={r['rule_value']}" for r in elig["matched_rules"]],
        "unmatched_rules": [f"{r['rule_type']}={r['rule_value']}" for r in elig["unmatched_rules"]],
    }


async def get_eligibility_breakdown(db: AsyncSession, scheme_id: UUID, farmer: Farmer) -> dict:
    result = await db.execute(
        select(Scheme)
        .options(selectinload(Scheme.eligibility_rules))
        .where(Scheme.id == scheme_id)
    )
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise NotFoundException("Scheme")

    farmer_data = _build_farmer_data(farmer)
    elig = evaluate_eligibility(scheme, farmer_data)

    return {
        "scheme_id": scheme.id,
        "scheme_name": scheme.name_en,
        "status": elig["status"],
        "score": elig["score"],
        "total_rules": elig["total_rules"],
        "mandatory_rules": elig["mandatory_rules"],
        "matched_mandatory": elig["matched_mandatory"],
        "matched_rules": elig["matched_rules"],
        "unmatched_rules": elig["unmatched_rules"],
    }


async def generate_scheme_form(
    db: AsyncSession,
    scheme_id: UUID,
    farmer: Farmer,
    generated_by: str = "farmer",
    agent_name: str | None = None,
    agent_session_id: UUID | None = None,
) -> dict:
    result = await db.execute(
        select(Scheme).where(Scheme.id == scheme_id)
    )
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise NotFoundException("Scheme")

    farmer_data_for_pdf = {
        "farmer_id": farmer.farmer_id,
        "name": farmer.name,
        "phone": farmer.phone,
        "district": farmer.district,
        "state": farmer.state,
        "pin_code": farmer.pin_code,
        "land_area": str(farmer.land_area),
        "land_unit": farmer.land_unit.value if hasattr(farmer.land_unit, 'value') else str(farmer.land_unit),
        "crops": [
            {"crop_name": c.crop_name, "season": c.season, "year": c.year}
            for c in (farmer.crops or []) if c.is_active
        ],
    }

    if farmer.profile:
        farmer_data_for_pdf["aadhaar_masked"] = farmer.profile.aadhaar_masked
        farmer_data_for_pdf["bank_ifsc"] = farmer.profile.bank_ifsc
        if farmer.profile.ownership_type:
            farmer_data_for_pdf["ownership_type"] = farmer.profile.ownership_type.value if hasattr(farmer.profile.ownership_type, 'value') else str(farmer.profile.ownership_type)
        if farmer.profile.irrigation_type:
            farmer_data_for_pdf["irrigation_type"] = farmer.profile.irrigation_type.value if hasattr(farmer.profile.irrigation_type, 'value') else str(farmer.profile.irrigation_type)

    scheme_data = {
        "name_en": scheme.name_en,
        "ministry": scheme.ministry,
        "benefit_type": scheme.benefit_type.value if hasattr(scheme.benefit_type, 'value') else str(scheme.benefit_type),
        "benefit_amount": scheme.benefit_amount,
        "documents_required": scheme.documents_required or [],
    }

    pdf_bytes, filename = build_scheme_form_pdf(
        farmer_data_for_pdf, scheme_data, generated_by, agent_name
    )

    file_key = f"forms/{farmer.farmer_id}/schemes/{scheme_id}/{filename}"
    await upload_bytes_to_s3(pdf_bytes, file_key, "application/pdf")

    form = GeneratedForm(
        farmer_id=farmer.id,
        scheme_id=scheme.id,
        file_key=file_key,
        file_name=filename,
        generated_by=GeneratedByType(generated_by),
        agent_session_id=agent_session_id,
    )
    db.add(form)
    await db.flush()

    logger.info("Scheme form generated: %s for farmer %s", filename, farmer.farmer_id)
    return {
        "file_key": file_key,
        "file_name": filename,
        "download_url": f"/files/{file_key}",
        "message": "Form generated successfully",
    }


async def create_scheme_reminder(
    db: AsyncSession,
    scheme_id: UUID,
    farmer: Farmer,
    channel: str,
) -> dict:
    result = await db.execute(
        select(Scheme).options(selectinload(Scheme.deadlines)).where(Scheme.id == scheme_id)
    )
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise NotFoundException("Scheme")

    today = date.today()
    nearest_deadline = None
    for dl in scheme.deadlines:
        if dl.close_date and dl.close_date > today:
            if nearest_deadline is None or dl.close_date < nearest_deadline:
                nearest_deadline = dl.close_date

    if not nearest_deadline:
        raise BadRequestException("No upcoming deadline found for this scheme")

    from datetime import timedelta
    remind_date = nearest_deadline - timedelta(days=3)
    if remind_date < today:
        remind_date = today

    reminder = Reminder(
        farmer_id=farmer.id,
        type=ReminderType.SCHEME,
        reference_id=scheme.id,
        remind_date=remind_date,
        channel=channel,
    )
    db.add(reminder)
    await db.flush()

    return {"message": f"Reminder set for {remind_date.isoformat()} via {channel}"}
