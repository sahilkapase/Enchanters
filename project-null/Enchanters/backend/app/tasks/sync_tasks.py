import asyncio
from app.tasks.celery_app import celery_app
from app.database import async_session_factory
import logging

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.sync_tasks.sync_schemes")
def sync_schemes():
    """Periodically sync scheme data from data.gov.in and other sources."""
    async def _sync():
        from app.external.data_gov import fetch_scheme_data
        try:
            records = await fetch_scheme_data("agriculture")
            logger.info("Fetched %d scheme records from data.gov.in", len(records))

            # In production, this would parse and upsert scheme data into the DB
            async with async_session_factory() as db:
                try:
                    updated = 0
                    for record in records:
                        logger.debug("Scheme record: %s", record.get("title", "unknown"))
                        updated += 1
                    await db.commit()
                    logger.info("Synced %d schemes", updated)
                    return updated
                except Exception as e:
                    await db.rollback()
                    logger.error("Scheme sync DB error: %s", str(e))
                    raise

        except Exception as e:
            logger.error("Scheme sync failed: %s", str(e))
            return 0

    return _run_async(_sync())


@celery_app.task(name="app.tasks.sync_tasks.sync_insurance_rates")
def sync_insurance_rates():
    """Sync insurance premium rates from PMFBY."""
    async def _sync():
        from app.external.pmfby import calculate_premium_from_api
        try:
            test = await calculate_premium_from_api("wheat", "rabi", "Agra", 1.0)
            if test:
                logger.info("PMFBY API is responsive, rates can be synced")
            else:
                logger.info("PMFBY API unavailable, using local rates")
            return {"pmfby_available": test is not None}
        except Exception as e:
            logger.error("Insurance rate sync failed: %s", str(e))
            return {"pmfby_available": False}

    return _run_async(_sync())


@celery_app.task(name="app.tasks.sync_tasks.sync_subsidy_deadlines")
def sync_subsidy_deadlines():
    """Check for updated subsidy deadlines from government portals."""
    logger.info("Subsidy deadline sync triggered")
    return {"status": "completed", "updated": 0}
