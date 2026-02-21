from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.notification import Reminder
from app.models.farmer import Farmer
from app.external.sms import send_sms
from app.external.email import send_reminder_email
import logging

logger = logging.getLogger(__name__)


async def get_due_reminders(db: AsyncSession) -> list[Reminder]:
    today = date.today()
    result = await db.execute(
        select(Reminder).where(
            Reminder.sent == False,
            Reminder.remind_date <= today,
        )
    )
    return list(result.scalars().all())


async def send_reminder(db: AsyncSession, reminder: Reminder) -> bool:
    farmer_result = await db.execute(
        select(Farmer).where(Farmer.id == reminder.farmer_id)
    )
    farmer = farmer_result.scalar_one_or_none()
    if not farmer:
        logger.warning("Farmer not found for reminder %s", reminder.id)
        return False

    channel = reminder.channel.value if hasattr(reminder.channel, 'value') else str(reminder.channel)
    message = f"KisaanSeva Reminder: You have an upcoming deadline for {reminder.type.value}. Please check the app."

    sent = False
    if channel in ("sms", "whatsapp"):
        sent = await send_sms(farmer.phone, message)
    elif channel == "email" and farmer.email:
        sent = await send_reminder_email(
            farmer.email,
            reminder.type.value,
            f"Deadline for {reminder.type.value}",
            reminder.remind_date.isoformat(),
        )

    if sent:
        reminder.sent = True
        reminder.sent_at = datetime.now(timezone.utc)
        await db.flush()
        logger.info("Reminder %s sent via %s", reminder.id, channel)

    return sent


async def process_due_reminders(db: AsyncSession) -> int:
    reminders = await get_due_reminders(db)
    sent_count = 0
    for reminder in reminders:
        if await send_reminder(db, reminder):
            sent_count += 1
    logger.info("Processed %d/%d due reminders", sent_count, len(reminders))
    return sent_count
