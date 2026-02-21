import asyncio
from datetime import datetime, timedelta, timezone
from app.tasks.celery_app import celery_app
from app.database import async_session_factory
from sqlalchemy import select, update
from app.models.agent import AgentSession
from app.core.constants import AgentSessionStatus, AGENT_SESSION_TTL_MINUTES
import logging

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.notification_tasks.process_reminders")
def process_reminders():
    """Process all due reminders and send notifications."""
    async def _process():
        async with async_session_factory() as db:
            try:
                from app.services.notification_service import process_due_reminders
                count = await process_due_reminders(db)
                await db.commit()
                logger.info("Processed %d reminders", count)
                return count
            except Exception as e:
                await db.rollback()
                logger.error("Reminder processing failed: %s", str(e))
                raise

    return _run_async(_process())


@celery_app.task(name="app.tasks.notification_tasks.expire_stale_sessions")
def expire_stale_sessions():
    """Mark agent sessions as expired if past TTL."""
    async def _expire():
        async with async_session_factory() as db:
            try:
                cutoff = datetime.now(timezone.utc) - timedelta(minutes=AGENT_SESSION_TTL_MINUTES)
                result = await db.execute(
                    update(AgentSession)
                    .where(
                        AgentSession.status == AgentSessionStatus.ACTIVE,
                        AgentSession.session_start.isnot(None),
                        AgentSession.session_start < cutoff,
                    )
                    .values(
                        status=AgentSessionStatus.EXPIRED,
                        session_end=datetime.now(timezone.utc),
                    )
                )
                await db.commit()
                logger.info("Expired %d stale sessions", result.rowcount)
                return result.rowcount
            except Exception as e:
                await db.rollback()
                logger.error("Session expiry failed: %s", str(e))
                raise

    return _run_async(_expire())


@celery_app.task(name="app.tasks.notification_tasks.send_sms_notification")
def send_sms_notification(phone: str, message: str):
    """Send a single SMS notification."""
    async def _send():
        from app.external.sms import send_sms
        return await send_sms(phone, message)

    return _run_async(_send())


@celery_app.task(name="app.tasks.notification_tasks.send_email_notification")
def send_email_notification(to: str, subject: str, body_html: str):
    """Send a single email notification."""
    async def _send():
        from app.external.email import send_email
        return await send_email(to, subject, body_html)

    return _run_async(_send())
