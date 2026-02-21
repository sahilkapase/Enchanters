import httpx
from typing import Optional
from app.config import settings
from app.core.exceptions import ExternalAPIException
import logging

logger = logging.getLogger(__name__)

PINCODE_CACHE: dict[str, dict] = {}


async def lookup_pincode(pincode: str) -> dict:
    """Look up district, state, and post offices from Indian PIN code using India Post API."""
    if pincode in PINCODE_CACHE:
        logger.debug("PIN code %s found in cache", pincode)
        return PINCODE_CACHE[pincode]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{settings.INDIA_POST_API_URL}/{pincode}")
            response.raise_for_status()
            data = response.json()

        if not data or data[0].get("Status") != "Success":
            return _fallback_pincode(pincode)

        post_offices = data[0].get("PostOffice", [])
        if not post_offices:
            return _fallback_pincode(pincode)

        first = post_offices[0]
        result = {
            "pincode": pincode,
            "district": first.get("District", ""),
            "state": first.get("State", ""),
            "country": first.get("Country", "India"),
            "post_offices": [
                {
                    "name": po.get("Name", ""),
                    "branch_type": po.get("BranchType", ""),
                    "delivery_status": po.get("DeliveryStatus", ""),
                    "division": po.get("Division", ""),
                    "region": po.get("Region", ""),
                    "block": po.get("Block", ""),
                }
                for po in post_offices
            ],
        }
        PINCODE_CACHE[pincode] = result
        return result

    except httpx.HTTPError as e:
        logger.warning("India Post API failed for PIN %s: %s", pincode, str(e))
        return _fallback_pincode(pincode)
    except Exception as e:
        logger.error("Unexpected error in India Post lookup: %s", str(e))
        return _fallback_pincode(pincode)


def _fallback_pincode(pincode: str) -> dict:
    """Fallback with basic state mapping when API is unavailable."""
    prefix_to_state = {
        "11": "Delhi", "12": "Haryana", "13": "Punjab", "14": "Himachal Pradesh",
        "15": "Jammu and Kashmir", "16": "Punjab", "17": "Himachal Pradesh",
        "18": "Jammu and Kashmir", "19": "Jammu and Kashmir",
        "20": "Uttar Pradesh", "21": "Uttar Pradesh", "22": "Uttar Pradesh",
        "23": "Uttar Pradesh", "24": "Uttar Pradesh", "25": "Uttar Pradesh",
        "26": "Uttarakhand", "27": "Uttar Pradesh", "28": "Uttar Pradesh",
        "30": "Rajasthan", "31": "Rajasthan", "32": "Rajasthan",
        "33": "Rajasthan", "34": "Rajasthan",
        "36": "Gujarat", "37": "Gujarat", "38": "Gujarat", "39": "Gujarat",
        "40": "Maharashtra", "41": "Maharashtra", "42": "Maharashtra",
        "43": "Maharashtra", "44": "Maharashtra", "45": "Madhya Pradesh",
        "46": "Madhya Pradesh", "47": "Madhya Pradesh", "48": "Madhya Pradesh",
        "49": "Chhattisgarh",
        "50": "Telangana", "51": "Andhra Pradesh", "52": "Andhra Pradesh",
        "53": "Andhra Pradesh",
        "56": "Karnataka", "57": "Karnataka", "58": "Karnataka", "59": "Karnataka",
        "60": "Tamil Nadu", "61": "Tamil Nadu", "62": "Tamil Nadu", "63": "Tamil Nadu",
        "64": "Tamil Nadu",
        "67": "Kerala", "68": "Kerala", "69": "Kerala",
        "70": "West Bengal", "71": "West Bengal", "72": "West Bengal", "73": "West Bengal",
        "74": "West Bengal",
        "75": "Odisha", "76": "Odisha", "77": "Odisha",
        "78": "Assam", "79": "Arunachal Pradesh",
        "80": "Bihar", "81": "Bihar", "82": "Bihar", "83": "Bihar", "84": "Bihar",
        "85": "Jharkhand",
    }
    prefix = pincode[:2]
    state = prefix_to_state.get(prefix, "")
    return {
        "pincode": pincode,
        "district": "",
        "state": state,
        "country": "India",
        "post_offices": [],
    }
