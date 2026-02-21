import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)


async def send_sms(phone: str, message: str) -> bool:
    """Send SMS via MSG91 or configured provider."""
    if settings.SMS_PROVIDER == "msg91":
        return await _send_via_msg91(phone, message)
    else:
        logger.warning("Unknown SMS provider: %s. SMS not sent.", settings.SMS_PROVIDER)
        return False


async def _send_via_msg91(phone: str, message: str) -> bool:
    if not settings.MSG91_AUTH_KEY:
        logger.info("MSG91 auth key not configured. SMS (dev mode): phone=%s, message=%s", phone, message)
        return True

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.msg91.com/api/v5/flow/",
                headers={
                    "authkey": settings.MSG91_AUTH_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "template_id": settings.MSG91_TEMPLATE_ID,
                    "sender": settings.MSG91_SENDER_ID,
                    "short_url": "0",
                    "mobiles": f"91{phone}",
                    "OTP": message,
                },
            )
            if response.status_code == 200:
                logger.info("SMS sent to %s***%s", phone[:2], phone[-2:])
                return True
            else:
                logger.error("MSG91 returned %d: %s", response.status_code, response.text)
                return False
    except Exception as e:
        logger.error("Failed to send SMS: %s", str(e))
        return False


async def send_otp_sms(phone: str, otp: str) -> bool:
    message = f"Your KisaanSeva OTP is {otp}. Valid for 5 minutes. Do not share."
    return await send_sms(phone, message)


async def send_agent_access_sms(phone: str, otp: str, agent_name: str, center: str, purpose: str) -> bool:
    message = (
        f"Agent {agent_name} at {center} requests access to your KisaanSeva account "
        f"for: {purpose}. OTP: {otp}. Valid for 5 minutes."
    )
    return await send_sms(phone, message)
