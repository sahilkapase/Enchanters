import random
import redis.asyncio as redis
from app.config import settings
from app.core.constants import OTP_LENGTH, OTP_TTL_SECONDS, OTP_MAX_ATTEMPTS, OTP_LOCKOUT_SECONDS, OTP_RATE_LIMIT_PER_HOUR
from app.core.exceptions import OTPExpiredException, OTPMaxAttemptsException, OTPRateLimitException
import logging

logger = logging.getLogger(__name__)

_redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def generate_otp() -> str:
    return "".join([str(random.randint(0, 9)) for _ in range(OTP_LENGTH)])


async def send_and_store_otp(phone: str, otp_type: str = "phone") -> str:
    r = await get_redis()

    rate_key = f"otp_rate:{phone}"
    current_count = await r.get(rate_key)
    if current_count and int(current_count) >= OTP_RATE_LIMIT_PER_HOUR:
        raise OTPRateLimitException()

    lockout_key = f"otp_lockout:{phone}:{otp_type}"
    if await r.exists(lockout_key):
        raise OTPMaxAttemptsException()

    otp = generate_otp()
    otp_key = f"otp:{phone}:{otp_type}"
    attempts_key = f"otp_attempts:{phone}:{otp_type}"

    await r.set(otp_key, otp, ex=OTP_TTL_SECONDS)
    await r.delete(attempts_key)

    pipe = r.pipeline()
    pipe.incr(rate_key)
    pipe.expire(rate_key, 3600)
    await pipe.execute()

    logger.info("OTP generated for %s (type=%s)", phone[-4:], otp_type)
    return otp


async def verify_otp(phone: str, otp: str, otp_type: str = "phone") -> bool:
    r = await get_redis()

    lockout_key = f"otp_lockout:{phone}:{otp_type}"
    if await r.exists(lockout_key):
        raise OTPMaxAttemptsException()

    otp_key = f"otp:{phone}:{otp_type}"
    stored_otp = await r.get(otp_key)

    if not stored_otp:
        raise OTPExpiredException()

    attempts_key = f"otp_attempts:{phone}:{otp_type}"
    attempts = await r.incr(attempts_key)
    await r.expire(attempts_key, OTP_TTL_SECONDS)

    if attempts > OTP_MAX_ATTEMPTS:
        await r.set(lockout_key, "1", ex=OTP_LOCKOUT_SECONDS)
        await r.delete(otp_key)
        await r.delete(attempts_key)
        raise OTPMaxAttemptsException()

    if stored_otp != otp:
        remaining = OTP_MAX_ATTEMPTS - attempts
        raise OTPExpiredException()

    await r.delete(otp_key)
    await r.delete(attempts_key)
    logger.info("OTP verified for %s (type=%s)", phone[-4:], otp_type)
    return True


async def store_refresh_token(subject: str, token: str, ttl_days: int = 7) -> None:
    r = await get_redis()
    key = f"refresh_token:{subject}"
    await r.set(key, token, ex=ttl_days * 86400)


async def is_refresh_token_valid(subject: str, token: str) -> bool:
    r = await get_redis()
    key = f"refresh_token:{subject}"
    stored = await r.get(key)
    return stored == token


async def revoke_refresh_token(subject: str) -> None:
    r = await get_redis()
    key = f"refresh_token:{subject}"
    await r.delete(key)
