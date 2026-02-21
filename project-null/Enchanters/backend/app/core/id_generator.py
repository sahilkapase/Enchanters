import random
import string
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

FARMER_ID_PREFIX = "KS"
FARMER_ID_RANDOM_LENGTH = 9
CHARSET = string.ascii_uppercase + string.digits


def _generate_random_id() -> str:
    random_part = "".join(random.choices(CHARSET, k=FARMER_ID_RANDOM_LENGTH))
    return f"{FARMER_ID_PREFIX}{random_part}"


async def generate_farmer_id(db: AsyncSession) -> str:
    from app.models.farmer import Farmer

    for _ in range(10):
        candidate = _generate_random_id()
        result = await db.execute(
            select(Farmer.id).where(Farmer.farmer_id == candidate)
        )
        if result.scalar_one_or_none() is None:
            logger.info("Generated farmer_id: %s", candidate)
            return candidate

    raise RuntimeError("Failed to generate unique farmer_id after 10 attempts")
