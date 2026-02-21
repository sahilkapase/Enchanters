import enum


class LandUnit(str, enum.Enum):
    ACRE = "acre"
    HECTARE = "hectare"
    BIGHA = "bigha"


class Season(str, enum.Enum):
    KHARIF = "kharif"
    RABI = "rabi"
    ZAID = "zaid"


class IrrigationType(str, enum.Enum):
    RAINFED = "rainfed"
    CANAL = "canal"
    BOREWELL = "borewell"
    DRIP = "drip"
    SPRINKLER = "sprinkler"


class OwnershipType(str, enum.Enum):
    OWNED = "owned"
    LEASED = "leased"
    SHARED = "shared"


class DocType(str, enum.Enum):
    AADHAAR = "aadhaar"
    RATION_CARD = "ration_card"
    LAND_PROOF = "land_proof"
    BANK_PASSBOOK = "bank_passbook"
    PHOTO = "photo"


class BenefitType(str, enum.Enum):
    CASH = "cash"
    SUBSIDY = "subsidy"
    INSURANCE = "insurance"
    EQUIPMENT = "equipment"


class RuleType(str, enum.Enum):
    CROP = "crop"
    LAND_MIN = "land_min"
    LAND_MAX = "land_max"
    STATE = "state"
    DISTRICT = "district"
    SEASON = "season"
    OWNERSHIP = "ownership"
    IRRIGATION = "irrigation"


class InsurancePlanType(str, enum.Enum):
    PMFBY = "pmfby"
    RWBCI = "rwbci"
    OTHER = "other"


class SubsidyCategory(str, enum.Enum):
    SEED = "seed"
    FERTILIZER = "fertilizer"
    EQUIPMENT = "equipment"
    IRRIGATION = "irrigation"
    ORGANIC = "organic"
    CREDIT = "credit"


class ReminderType(str, enum.Enum):
    SCHEME = "scheme"
    SUBSIDY = "subsidy"
    INSURANCE = "insurance"


class ReminderChannel(str, enum.Enum):
    SMS = "sms"
    WHATSAPP = "whatsapp"
    EMAIL = "email"


class CenterType(str, enum.Enum):
    CSC = "csc"
    JAN_SUVIDHA = "jan_suvidha"
    BANK = "bank"
    OTHER = "other"


class AgentSessionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    ENDED = "ended"


class GeneratedByType(str, enum.Enum):
    FARMER = "farmer"
    AGENT = "agent"


class EligibilityStatus(str, enum.Enum):
    ELIGIBLE = "eligible"
    PARTIAL = "partial"
    NOT_ELIGIBLE = "not_eligible"


LAND_CONVERSION = {
    LandUnit.ACRE: 1.0,
    LandUnit.HECTARE: 2.47105,
    LandUnit.BIGHA: 0.6198,
}

ALLOWED_DOC_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB

OTP_LENGTH = 6
OTP_TTL_SECONDS = 300  # 5 minutes
OTP_MAX_ATTEMPTS = 3
OTP_LOCKOUT_SECONDS = 900  # 15 minutes
OTP_RATE_LIMIT_PER_HOUR = 5

AGENT_SESSION_TTL_MINUTES = 30

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry",
]

MAJOR_CROPS = [
    "wheat", "rice", "maize", "bajra", "jowar", "ragi", "barley",
    "sugarcane", "cotton", "jute", "tobacco", "groundnut", "soybean",
    "mustard", "sunflower", "sesame", "linseed", "castor",
    "chickpea", "pigeon pea", "moong", "urad", "lentil", "pea",
    "potato", "onion", "tomato", "brinjal", "cauliflower", "cabbage",
    "mango", "banana", "apple", "orange", "grape", "guava",
    "tea", "coffee", "rubber", "coconut", "arecanut", "cardamom",
    "turmeric", "ginger", "chilli", "coriander", "cumin",
]
