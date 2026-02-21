from app.external.india_post import lookup_pincode
from app.external.lgd import get_states, get_districts, get_districts_from_api
import logging

logger = logging.getLogger(__name__)


async def get_pin_details(pincode: str) -> dict:
    return await lookup_pincode(pincode)


def list_states() -> list[str]:
    return get_states()


async def list_districts(state: str) -> list[str]:
    districts = await get_districts_from_api(state)
    if not districts:
        districts = get_districts(state)
    return districts
