"""
Seed script: Load seed data (schemes, insurance plans, subsidies) into the database.
Usage: python -m seed_data.seed
"""

import asyncio
import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from app.database import async_session_factory, engine, Base
from app.models import (
    Scheme, SchemeEligibility, SchemeDeadline,
    InsurancePlan, Subsidy, Agent,
)
from app.core.constants import (
    BenefitType, RuleType, InsurancePlanType, SubsidyCategory,
)
from app.core.security import hash_password

SEED_DIR = Path(__file__).parent


def load_json(filename: str) -> list[dict]:
    with open(SEED_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_schemes(db):
    data = load_json("schemes.json")
    existing = await db.execute(select(Scheme.name_en))
    existing_names = {row[0] for row in existing.all()}

    count = 0
    for item in data:
        if item["name_en"] in existing_names:
            print(f"  Skipping (exists): {item['name_en']}")
            continue

        scheme = Scheme(
            name_en=item["name_en"],
            name_hi=item.get("name_hi"),
            ministry=item.get("ministry"),
            description_en=item.get("description_en"),
            description_hi=item.get("description_hi"),
            benefit_type=BenefitType(item["benefit_type"]),
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
            db.add(SchemeEligibility(
                scheme_id=scheme.id,
                rule_type=RuleType(rule["rule_type"]),
                rule_value=rule["rule_value"],
                is_mandatory=rule.get("is_mandatory", True),
            ))

        for dl in item.get("deadlines", []):
            db.add(SchemeDeadline(
                scheme_id=scheme.id,
                season=dl.get("season"),
                year=dl.get("year"),
                open_date=date.fromisoformat(dl["open_date"]) if dl.get("open_date") else None,
                close_date=date.fromisoformat(dl["close_date"]) if dl.get("close_date") else None,
                state=dl.get("state"),
            ))

        count += 1
        print(f"  Added scheme: {item['name_en']}")

    await db.flush()
    return count


async def seed_insurance(db):
    data = load_json("insurance_plans.json")
    existing = await db.execute(select(InsurancePlan.name_en))
    existing_names = {row[0] for row in existing.all()}

    count = 0
    for item in data:
        if item["name_en"] in existing_names:
            print(f"  Skipping (exists): {item['name_en']}")
            continue

        plan = InsurancePlan(
            name_en=item["name_en"],
            name_hi=item.get("name_hi"),
            plan_type=InsurancePlanType(item["plan_type"]),
            description_en=item.get("description_en"),
            description_hi=item.get("description_hi"),
            coverage=item.get("coverage"),
            premium_info=item.get("premium_info"),
            eligibility=item.get("eligibility"),
            how_to_enroll=item.get("how_to_enroll"),
            is_active=item.get("is_active", True),
        )
        db.add(plan)
        count += 1
        print(f"  Added insurance plan: {item['name_en']}")

    await db.flush()
    return count


async def seed_subsidies(db):
    data = load_json("subsidies.json")
    existing = await db.execute(select(Subsidy.name_en))
    existing_names = {row[0] for row in existing.all()}

    count = 0
    for item in data:
        if item["name_en"] in existing_names:
            print(f"  Skipping (exists): {item['name_en']}")
            continue

        subsidy = Subsidy(
            name_en=item["name_en"],
            name_hi=item.get("name_hi"),
            category=SubsidyCategory(item["category"]),
            description_en=item.get("description_en"),
            description_hi=item.get("description_hi"),
            benefit_amount=item.get("benefit_amount"),
            eligibility=item.get("eligibility"),
            open_date=date.fromisoformat(item["open_date"]) if item.get("open_date") else None,
            close_date=date.fromisoformat(item["close_date"]) if item.get("close_date") else None,
            state=item.get("state"),
            is_active=item.get("is_active", True),
        )
        db.add(subsidy)
        count += 1
        print(f"  Added subsidy: {item['name_en']}")

    await db.flush()
    return count


async def seed_demo_agent(db):
    existing = await db.execute(select(Agent).where(Agent.phone == "9999999999"))
    if existing.scalar_one_or_none():
        print("  Demo agent already exists")
        return 0

    agent = Agent(
        name="Demo Agent",
        phone="9999999999",
        email="agent@kisaanseva.in",
        center_name="KisaanSeva Demo CSC",
        center_type="csc",
        password_hash=hash_password("agent123"),
        is_active=True,
    )
    db.add(agent)
    await db.flush()
    print("  Added demo agent (phone: 9999999999, password: agent123)")
    return 1


async def main():
    print("=" * 60)
    print("KisaanSeva Seed Data Loader")
    print("=" * 60)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("\nDatabase tables created/verified.\n")

    async with async_session_factory() as db:
        try:
            print("[1/4] Seeding schemes...")
            scheme_count = await seed_schemes(db)
            print(f"  -> {scheme_count} schemes added\n")

            print("[2/4] Seeding insurance plans...")
            ins_count = await seed_insurance(db)
            print(f"  -> {ins_count} insurance plans added\n")

            print("[3/4] Seeding subsidies...")
            sub_count = await seed_subsidies(db)
            print(f"  -> {sub_count} subsidies added\n")

            print("[4/4] Seeding demo agent...")
            agent_count = await seed_demo_agent(db)
            print(f"  -> {agent_count} agent(s) added\n")

            await db.commit()
            print("=" * 60)
            print("Seed complete!")
            print(f"  Schemes: {scheme_count}")
            print(f"  Insurance Plans: {ins_count}")
            print(f"  Subsidies: {sub_count}")
            print(f"  Agents: {agent_count}")
            print("=" * 60)

        except Exception as e:
            await db.rollback()
            print(f"\nERROR: {e}")
            raise

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
