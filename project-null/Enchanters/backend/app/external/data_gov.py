import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)


async def fetch_agriculture_data(resource_id: str, filters: dict | None = None, limit: int = 100) -> dict:
    """Fetch data from data.gov.in API."""
    try:
        params = {
            "api-key": settings.DATA_GOV_API_KEY,
            "format": "json",
            "limit": limit,
        }
        if filters:
            for k, v in filters.items():
                params[f"filters[{k}]"] = v

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{settings.DATA_GOV_API_URL}/{resource_id}",
                params=params,
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        logger.warning("data.gov.in API failed: %s", str(e))
        return {"status": "error", "message": str(e), "records": []}
    except Exception as e:
        logger.error("Unexpected error fetching from data.gov.in: %s", str(e))
        return {"status": "error", "message": str(e), "records": []}


async def fetch_scheme_data(scheme_keyword: str) -> list[dict]:
    """Search for government scheme data."""
    resource_ids = [
        "9ef84268-d588-465a-a308-a864a43d0070",  # Agriculture schemes
    ]
    all_records = []
    for rid in resource_ids:
        data = await fetch_agriculture_data(rid, limit=50)
        records = data.get("records", [])
        all_records.extend(records)
    return all_records
