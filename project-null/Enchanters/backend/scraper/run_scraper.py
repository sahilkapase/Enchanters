"""
run_scraper.py — Comprehensive Government Scheme / Insurance / Subsidy Scraper
==============================================================================
Fetches data from:
  1. seed_data/ JSON files (existing curated data)
  2. scraper/data/ extended JSON files (30+ additional central & state schemes)
  3. data.gov.in API  (live government datasets where accessible)

Upserts everything into NeonDB so any user request can be served directly from
the database without calling external APIs at runtime.

Usage (from backend/ directory):
    python -m scraper.run_scraper
    python -m scraper.run_scraper --source all        # default: all sources
    python -m scraper.run_scraper --source local      # only JSON files
    python -m scraper.run_scraper --source api        # only live API fetch

Environment: reads backend/.env automatically.
"""

import asyncio
import json
import sys
import argparse
import httpx
from datetime import date, datetime
from pathlib import Path

# Force UTF-8 output on Windows to avoid cp1252 encoding errors
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent          # backend/
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env", override=True)

from sqlalchemy import select, text
from app.database import async_session_factory, engine, Base
from app.models import Scheme, SchemeEligibility, SchemeDeadline, InsurancePlan, Subsidy
from app.core.constants import BenefitType, RuleType, InsurancePlanType, SubsidyCategory
import app.models  # noqa: F401 – register all models

SEED_DIR   = ROOT / "seed_data"
EXTEND_DIR = ROOT / "scraper" / "data"

# ── data.gov.in resource IDs relevant to agriculture ─────────────────────────
DATA_GOV_RESOURCES = [
    # Central Government Schemes list (NIC)
    {"id": "352b9082-b85a-4c47-a33c-54a7e29a3ec5", "label": "Central Govt Schemes"},
    # Agriculture schemes under DAC
    {"id": "9ef84268-d588-465a-a308-a864a43d0070", "label": "Agriculture data"},
    # PM-KISAN beneficiary statistics
    {"id": "7e8a96c4-b1f2-4e3a-8f7b-3e9f4a5b6c7d", "label": "PM-KISAN stats"},
]

BOLD  = ""
GREEN = ""
CYAN  = ""
WARN  = ""
FAIL  = ""
RESET = ""


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _print_section(title: str):
    print(f"\n{'=' * 58}")
    print(f"  {title}")
    print(f"{'=' * 58}")


def _load_json(path: Path) -> list[dict]:
    if not path.exists():
        print(f"  WARN  File not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse_date(s: str | None) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Database helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _existing_names(db, model, col) -> set[str]:
    result = await db.execute(select(col))
    return {row[0] for row in result.all()}


async def upsert_scheme(db, item: dict, existing: set[str]) -> bool:
    """Insert one scheme record. Returns True if inserted, False if skipped."""
    name = item.get("name_en", "").strip()
    if not name or name in existing:
        return False

    benefit_raw = item.get("benefit_type", "cash")
    try:
        benefit = BenefitType(benefit_raw)
    except ValueError:
        benefit = BenefitType.CASH

    scheme = Scheme(
        name_en=name,
        name_hi=item.get("name_hi"),
        ministry=item.get("ministry"),
        description_en=item.get("description_en"),
        description_hi=item.get("description_hi"),
        benefit_type=benefit,
        benefit_amount=item.get("benefit_amount"),
        apply_url=item.get("apply_url"),
        documents_required=item.get("documents_required", []),
        how_to_apply=item.get("how_to_apply"),
        is_active=item.get("is_active", True),
        source_url=item.get("source_url"),
    )
    db.add(scheme)
    await db.flush()

    for rule in item.get("eligibility_rules", []):
        try:
            rt = RuleType(rule["rule_type"])
        except (ValueError, KeyError):
            continue
        db.add(SchemeEligibility(
            scheme_id=scheme.id,
            rule_type=rt,
            rule_value=str(rule.get("rule_value", "")),
            is_mandatory=rule.get("is_mandatory", True),
        ))

    VALID_SEASONS = {"kharif", "rabi", "zaid"}
    for dl in item.get("deadlines", []):
        season_val = dl.get("season")
        if season_val and season_val not in VALID_SEASONS:
            season_val = None  # skip invalid season enums
        db.add(SchemeDeadline(
            scheme_id=scheme.id,
            season=season_val,
            year=dl.get("year"),
            open_date=_parse_date(dl.get("open_date")),
            close_date=_parse_date(dl.get("close_date")),
            state=dl.get("state"),
        ))

    existing.add(name)
    return True


async def upsert_insurance(db, item: dict, existing: set[str]) -> bool:
    name = item.get("name_en", "").strip()
    if not name or name in existing:
        return False

    try:
        plan_type = InsurancePlanType(item.get("plan_type", "other"))
    except ValueError:
        plan_type = InsurancePlanType.OTHER

    db.add(InsurancePlan(
        name_en=name,
        name_hi=item.get("name_hi"),
        plan_type=plan_type,
        description_en=item.get("description_en"),
        description_hi=item.get("description_hi"),
        coverage=item.get("coverage"),
        premium_info=item.get("premium_info"),
        eligibility=item.get("eligibility"),
        how_to_enroll=item.get("how_to_enroll"),
        is_active=item.get("is_active", True),
    ))
    existing.add(name)
    return True


async def upsert_subsidy(db, item: dict, existing: set[str]) -> bool:
    name = item.get("name_en", "").strip()
    if not name or name in existing:
        return False

    try:
        cat = SubsidyCategory(item.get("category", "seed"))
    except ValueError:
        cat = SubsidyCategory.SEED

    db.add(Subsidy(
        name_en=name,
        name_hi=item.get("name_hi"),
        category=cat,
        description_en=item.get("description_en"),
        description_hi=item.get("description_hi"),
        benefit_amount=item.get("benefit_amount"),
        eligibility=item.get("eligibility", {}),
        open_date=_parse_date(item.get("open_date")),
        close_date=_parse_date(item.get("close_date")),
        state=item.get("state"),
        is_active=item.get("is_active", True),
    ))
    existing.add(name)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# data.gov.in live fetch
# ─────────────────────────────────────────────────────────────────────────────

async def fetch_datagov_schemes(api_key: str, api_url: str) -> list[dict]:
    """Try to pull scheme records from data.gov.in. Returns empty list on failure."""
    results: list[dict] = []
    if not api_key or api_key.startswith("your-"):
        print(f"  WARN  DATA_GOV_API_KEY not set -- skipping live fetch")
        return results

    async with httpx.AsyncClient(timeout=20.0) as client:
        for res in DATA_GOV_RESOURCES:
            url = f"{api_url}/{res['id']}"
            params = {"api-key": api_key, "format": "json", "limit": 100}
            label = res["label"]
            try:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    body = resp.json()
                    records = body.get("records", body.get("data", []))
                    print(f"  OK  {label}: {len(records)} records fetched")
                    # Attempt to parse records into our scheme format
                    for rec in records:
                        scheme = _datagov_record_to_scheme(rec)
                        if scheme:
                            results.append(scheme)
                elif resp.status_code in (404, 400):
                    print(f"  WARN  {label}: resource not found (404). Skipping.")
                else:
                    print(f"  WARN  {label}: HTTP {resp.status_code}")
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                print(f"  WARN  {label}: network error ({e}) -- skipping")

    return results


def _datagov_record_to_scheme(rec: dict) -> dict | None:
    """Map a data.gov.in record to our scheme format. Returns None if unmappable."""
    # Try common field name patterns from data.gov.in datasets
    name = (
        rec.get("scheme_name") or rec.get("Scheme_Name") or rec.get("schemeName")
        or rec.get("name") or rec.get("Name") or rec.get("title") or ""
    ).strip()

    if not name or len(name) < 5:
        return None

    desc = (
        rec.get("description") or rec.get("Description")
        or rec.get("scheme_description") or rec.get("Scheme_Description")
        or rec.get("objective") or rec.get("Objective") or ""
    ).strip()

    ministry = (
        rec.get("ministry") or rec.get("Ministry") or rec.get("department")
        or rec.get("Department") or ""
    ).strip()

    apply_url = (
        rec.get("url") or rec.get("URL") or rec.get("website")
        or rec.get("Website") or rec.get("link") or ""
    ).strip()

    benefit = rec.get("benefit_type") or rec.get("schemeType") or "subsidy"
    if benefit.lower() in ("cash", "direct benefit transfer", "dbt"):
        benefit = "cash"
    elif benefit.lower() in ("insurance",):
        benefit = "insurance"
    elif benefit.lower() in ("equipment", "machinery"):
        benefit = "equipment"
    else:
        benefit = "subsidy"

    return {
        "name_en": name,
        "name_hi": None,
        "ministry": ministry or "Government of India",
        "description_en": desc or f"{name} — Government of India scheme",
        "description_hi": None,
        "benefit_type": benefit,
        "benefit_amount": rec.get("benefit_amount") or rec.get("financial_assistance") or "",
        "apply_url": apply_url,
        "documents_required": [],
        "how_to_apply": rec.get("how_to_apply") or rec.get("procedure") or "",
        "is_active": True,
        "source_url": apply_url or "https://www.india.gov.in/",
        "eligibility_rules": [],
        "deadlines": [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main orchestrator
# ─────────────────────────────────────────────────────────────────────────────

async def run(source: str = "all"):
    import os

    _print_section("KisaanSeva — Government Data Scraper & DB Seeder")
    print(f"  Source mode : {BOLD}{source}{RESET}")

    # ── Ensure tables exist ───────────────────────────────────────────────────
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"  OK  Database tables verified")

    async with async_session_factory() as db:

        # ── Pre-load existing names to avoid duplicates ───────────────────────
        existing_schemes   = await _existing_names(db, Scheme,       Scheme.name_en)
        existing_insurance = await _existing_names(db, InsurancePlan, InsurancePlan.name_en)
        existing_subsidies = await _existing_names(db, Subsidy,       Subsidy.name_en)

        print(f"\n  Already in DB → "
              f"{len(existing_schemes)} schemes, "
              f"{len(existing_insurance)} insurance plans, "
              f"{len(existing_subsidies)} subsidies")

        total_s = total_i = total_sub = 0

        # ── 1. Seed data JSON files ───────────────────────────────────────────
        if source in ("all", "local"):
            _print_section("Loading seed_data/ JSON files")

            for scheme in _load_json(SEED_DIR / "schemes.json"):
                if await upsert_scheme(db, scheme, existing_schemes):
                    total_s += 1

            for plan in _load_json(SEED_DIR / "insurance_plans.json"):
                if await upsert_insurance(db, plan, existing_insurance):
                    total_i += 1

            for sub in _load_json(SEED_DIR / "subsidies.json"):
                if await upsert_subsidy(db, sub, existing_subsidies):
                    total_sub += 1

            print(f"  Seed data  →  +{total_s} schemes, +{total_i} insurance, +{total_sub} subsidies")

        # ── 2. Extended data JSON files ───────────────────────────────────────
        if source in ("all", "local"):
            _print_section("Loading scraper/data/ extended JSON files")

            s2 = i2 = sub2 = 0
            for scheme in _load_json(EXTEND_DIR / "extended_schemes.json"):
                if await upsert_scheme(db, scheme, existing_schemes):
                    s2 += 1

            # Additional batch of government schemes (state + central)
            for scheme in _load_json(EXTEND_DIR / "more_schemes.json"):
                if await upsert_scheme(db, scheme, existing_schemes):
                    s2 += 1

            for plan in _load_json(EXTEND_DIR / "extended_insurance.json"):
                if await upsert_insurance(db, plan, existing_insurance):
                    i2 += 1

            for sub in _load_json(EXTEND_DIR / "extended_subsidies.json"):
                if await upsert_subsidy(db, sub, existing_subsidies):
                    sub2 += 1

            total_s += s2; total_i += i2; total_sub += sub2
            print(f"  Extended   →  +{s2} schemes, +{i2} insurance, +{sub2} subsidies")

        # ── 3. data.gov.in live API fetch ─────────────────────────────────────
        if source in ("all", "api"):
            _print_section("Fetching live data from data.gov.in API")

            api_key = os.environ.get("DATA_GOV_API_KEY", "")
            api_url = os.environ.get("DATA_GOV_API_URL", "https://api.data.gov.in/resource")

            live_schemes = await fetch_datagov_schemes(api_key, api_url)

            s3 = 0
            for scheme in live_schemes:
                if await upsert_scheme(db, scheme, existing_schemes):
                    s3 += 1

            total_s += s3
            print(f"  Live API   →  +{s3} schemes added from data.gov.in")

        # ── Commit all ────────────────────────────────────────────────────────
        await db.commit()

    # ── Final summary ─────────────────────────────────────────────────────────
    _print_section("Scrape + Seed Complete")

    async with async_session_factory() as db:
        count_s   = (await db.execute(text("SELECT COUNT(*) FROM schemes"))).scalar()
        count_i   = (await db.execute(text("SELECT COUNT(*) FROM insurance_plans"))).scalar()
        count_sub = (await db.execute(text("SELECT COUNT(*) FROM subsidies"))).scalar()
        count_eli = (await db.execute(text("SELECT COUNT(*) FROM scheme_eligibility"))).scalar()
        count_dl  = (await db.execute(text("SELECT COUNT(*) FROM scheme_deadlines"))).scalar()

    print(f"""
  NeonDB now contains:
  +----------------------------------+----------+
  | Table                            |  Records |
  +----------------------------------+----------+
  | schemes                          |  {count_s:>6}   |
  | scheme_eligibility               |  {count_eli:>6}   |
  | scheme_deadlines                 |  {count_dl:>6}   |
  | insurance_plans                  |  {count_i:>6}   |
  | subsidies                        |  {count_sub:>6}   |
  +----------------------------------+----------+

  New records inserted this run:
    schemes     +{total_s}
    insurance   +{total_i}
    subsidies   +{total_sub}
""")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KisaanSeva government data scraper")
    parser.add_argument(
        "--source",
        choices=["all", "local", "api"],
        default="all",
        help="Data source: all (default), local (JSON only), api (data.gov.in only)",
    )
    args = parser.parse_args()
    asyncio.run(run(source=args.source))
