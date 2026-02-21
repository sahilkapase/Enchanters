import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)

PREMIUM_RATES = {
    "kharif": {"food_grains_oilseeds": 2.0, "commercial_horticultural": 5.0},
    "rabi": {"food_grains_oilseeds": 1.5, "commercial_horticultural": 5.0},
    "zaid": {"food_grains_oilseeds": 2.0, "commercial_horticultural": 5.0},
}

SUM_INSURED_PER_HECTARE = {
    "wheat": 37_000, "rice": 40_000, "maize": 25_000, "bajra": 20_000,
    "jowar": 18_000, "ragi": 22_000, "barley": 25_000,
    "sugarcane": 80_000, "cotton": 45_000, "jute": 30_000,
    "groundnut": 40_000, "soybean": 35_000, "mustard": 38_000,
    "sunflower": 32_000, "sesame": 35_000,
    "chickpea": 30_000, "pigeon pea": 28_000, "moong": 30_000,
    "urad": 28_000, "lentil": 30_000,
    "potato": 50_000, "onion": 55_000, "tomato": 60_000,
    "mango": 70_000, "banana": 65_000, "apple": 90_000,
}

COMMERCIAL_CROPS = {"sugarcane", "cotton", "jute", "tobacco", "mango", "banana", "apple", "orange", "grape", "guava", "tea", "coffee", "rubber", "coconut"}

INSURANCE_COMPANIES = [
    "Agriculture Insurance Company of India",
    "ICICI Lombard General Insurance",
    "HDFC ERGO General Insurance",
    "Bajaj Allianz General Insurance",
    "Reliance General Insurance",
    "SBI General Insurance",
]


async def calculate_premium_from_api(crop: str, season: str, district: str, land_area_hectares: float) -> dict | None:
    """Try to calculate premium from PMFBY API. Returns None if API unavailable."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.PMFBY_API_URL}/premium-calculator",
                json={
                    "crop": crop,
                    "season": season,
                    "district": district,
                    "area_hectares": land_area_hectares,
                },
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "sum_insured": data.get("sum_insured", 0),
                    "farmer_premium": data.get("farmer_premium", 0),
                    "govt_subsidy": data.get("govt_subsidy", 0),
                    "insurance_company": data.get("insurance_company", ""),
                    "premium_rate_percent": data.get("premium_rate", 0),
                    "source": "pmfby_api",
                }
    except Exception as e:
        logger.warning("PMFBY API unavailable: %s", str(e))

    return None


def calculate_premium_local(crop: str, season: str, district: str, land_area_hectares: float) -> dict:
    """Local fallback premium calculation based on standard PMFBY rates."""
    crop_lower = crop.lower()
    season_lower = season.lower()

    si_per_ha = SUM_INSURED_PER_HECTARE.get(crop_lower, 30_000)
    total_sum_insured = si_per_ha * land_area_hectares

    is_commercial = crop_lower in COMMERCIAL_CROPS
    crop_category = "commercial_horticultural" if is_commercial else "food_grains_oilseeds"
    season_rates = PREMIUM_RATES.get(season_lower, PREMIUM_RATES["kharif"])
    rate = season_rates.get(crop_category, 2.0)

    farmer_premium = total_sum_insured * (rate / 100)
    govt_subsidy = total_sum_insured * ((min(rate, 5.0) if is_commercial else rate) / 100) * 1.5

    import random
    company = random.choice(INSURANCE_COMPANIES)

    return {
        "sum_insured": round(total_sum_insured, 2),
        "farmer_premium": round(farmer_premium, 2),
        "govt_subsidy": round(govt_subsidy, 2),
        "insurance_company": company,
        "premium_rate_percent": rate,
        "source": "local_calculation",
    }
