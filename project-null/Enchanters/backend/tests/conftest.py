"""
conftest.py — shared test fixtures and dependency overrides.

Environment variables that would cause startup failures (bad FERNET_KEY,
malformed DATABASE_URL) are patched into os.environ *before* any app
module is imported, so the Settings singleton picks up valid values.
"""

import os
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

# ── Patch broken .env values before app imports ──────────────────────────────
# A valid Fernet key (32 url-safe base64-encoded bytes).
os.environ["FERNET_KEY"] = "ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg="
# A syntactically valid DB URL so SQLAlchemy can create the engine object
# (no real connection is made because get_db is overridden in every test).
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/testdb"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-for-testing-only-minimum-32"
# ─────────────────────────────────────────────────────────────────────────────

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.deps import get_db, get_current_farmer, get_current_agent
from app.core.security import create_access_token, create_refresh_token

# ── Stable UUIDs used across the whole test session ──────────────────────────
FARMER_UUID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
FARMER_KID = "KS-MH-2025-001"
AGENT_UUID = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_farmer() -> MagicMock:
    """Return a MagicMock that looks like a fully-loaded Farmer ORM object."""
    farmer = MagicMock()
    farmer.id = FARMER_UUID
    farmer.farmer_id = FARMER_KID
    farmer.name = "Raju Test"
    farmer.phone = "9876543210"
    farmer.email = "raju@test.com"
    farmer.email_verified = False
    farmer.phone_verified = True
    farmer.pin_code = "380001"
    farmer.district = "Ahmedabad"
    farmer.state = "Gujarat"
    farmer.land_area = 5.0
    farmer.land_unit = "acre"
    farmer.language_pref = "hi"
    farmer.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    farmer.updated_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    farmer.profile = None
    farmer.crops = []
    farmer.documents = []
    farmer.reminders = []
    farmer.generated_forms = []
    return farmer


def _make_agent() -> MagicMock:
    agent = MagicMock()
    agent.id = AGENT_UUID
    agent.name = "Test Agent"
    agent.center_name = "CSC Centre 1"
    return agent


def make_farmer_token() -> str:
    return create_access_token(
        str(FARMER_UUID),
        extra_claims={"farmer_id": FARMER_KID, "role": "farmer"},
    )


def make_agent_token() -> str:
    return create_access_token(
        str(AGENT_UUID),
        extra_claims={"role": "agent"},
    )


# ── Module-level singletons shared by all tests ───────────────────────────────
TEST_FARMER = _make_farmer()
TEST_AGENT = _make_agent()


# ── DB override  ──────────────────────────────────────────────────────────────

async def _override_get_db():
    """Yield a no-op mock session so no real DB connection is needed."""
    db = AsyncMock()
    # execute().return_value must be a plain MagicMock so that callers can do
    # result.scalars().all() / result.scalar_one_or_none() without getting
    # coroutines back (which would happen if the return_value were AsyncMock).
    mock_result = MagicMock()
    db.execute = AsyncMock(return_value=mock_result)
    db.delete = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.close = AsyncMock()
    db.refresh = AsyncMock()
    yield db


async def _override_get_current_farmer():
    return TEST_FARMER


async def _override_get_current_agent():
    return TEST_AGENT


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
async def client():
    """HTTP test client with DB and auth dependencies overridden."""
    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_farmer] = _override_get_current_farmer
    app.dependency_overrides[get_current_agent] = _override_get_current_agent

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def unauth_client():
    """HTTP test client where ONLY get_db is overridden.

    'get_current_farmer' / 'get_current_agent' are left as-is so HTTPBearer
    rejects requests that arrive without a valid Authorization header (403).
    """
    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict:
    """Bearer token for the test farmer."""
    return {"Authorization": f"Bearer {make_farmer_token()}"}


@pytest.fixture
def agent_auth_headers() -> dict:
    """Bearer token for the test agent."""
    return {"Authorization": f"Bearer {make_agent_token()}"}


@pytest.fixture
def test_farmer() -> MagicMock:
    return TEST_FARMER


@pytest.fixture
def test_agent() -> MagicMock:
    return TEST_AGENT
