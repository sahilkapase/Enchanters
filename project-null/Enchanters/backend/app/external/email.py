import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
from app.config import settings
import logging

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, body_html: str) -> bool:
    """Send email via SMTP (runs in thread pool to avoid blocking)."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info("SMTP not configured. Email (dev mode): to=%s, subject=%s", to, subject)
        return True

    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, _send_email_sync, to, subject, body_html
        )
        return result
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to, str(e))
        return False


def _send_email_sync(to: str, subject: str, body_html: str) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, to, msg.as_string())
        logger.info("Email sent to %s", to)
    return True


async def send_otp_email(to: str, otp: str) -> bool:
    subject = "KisaanSeva - Email Verification OTP"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #2e7d32;">KisaanSeva</h2>
        <p>Your email verification OTP is:</p>
        <h1 style="color: #1b5e20; letter-spacing: 4px;">{otp}</h1>
        <p>This OTP is valid for 5 minutes. Do not share it with anyone.</p>
        <hr>
        <p style="color: #888; font-size: 12px;">KisaanSeva - Empowering Indian Farmers</p>
    </body>
    </html>
    """
    return await send_email(to, subject, body)


async def send_reminder_email(to: str, reminder_type: str, item_name: str, deadline: str) -> bool:
    subject = f"KisaanSeva - Reminder: {item_name}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #2e7d32;">KisaanSeva Reminder</h2>
        <p>This is a reminder about: <strong>{item_name}</strong></p>
        <p>Type: {reminder_type}</p>
        <p>Deadline: {deadline}</p>
        <p>Please take action before the deadline.</p>
        <hr>
        <p style="color: #888; font-size: 12px;">KisaanSeva - Empowering Indian Farmers</p>
    </body>
    </html>
    """
    return await send_email(to, subject, body)
