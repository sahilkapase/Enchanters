"""
test_connectivity.py — Live connectivity checks for all external services.

Run from the backend/ directory:
    pytest tests/test_connectivity.py -v -s

These tests make REAL network calls and require valid credentials.
Tests are automatically skipped when credentials are placeholder values.
"""

import os
import sys
import asyncio
import socket
import smtplib
from base64 import b64encode

import pytest
import httpx

# ── Read values DIRECTLY from .env — bypasses both conftest patches
#    and the cached settings singleton (which may have test values). ───────────
from dotenv import dotenv_values as _dv

_ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")
_env = _dv(_ENV_PATH)


class _LiveSettings:
    """Thin wrapper so tests can use the same `settings.X` style."""
    DATABASE_URL  = _env.get("DATABASE_URL", "")
    REDIS_URL     = _env.get("REDIS_URL", "redis://localhost:6379/0")
    INDIA_POST_API_URL = _env.get("INDIA_POST_API_URL", "https://api.postalpincode.in/pincode")
    DATA_GOV_API_KEY   = _env.get("DATA_GOV_API_KEY", "")
    DATA_GOV_API_URL   = _env.get("DATA_GOV_API_URL", "https://api.data.gov.in/resource")
    PMFBY_API_URL      = _env.get("PMFBY_API_URL", "https://pmfby.gov.in/api")
    LGD_API_URL        = _env.get("LGD_API_URL", "https://lgdirectory.gov.in/api")
    MSG91_AUTH_KEY     = _env.get("MSG91_AUTH_KEY", "")
    SMTP_HOST          = _env.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT          = int(_env.get("SMTP_PORT", "587"))
    SMTP_USER          = _env.get("SMTP_USER", "")
    SMTP_PASSWORD      = _env.get("SMTP_PASSWORD", "")


settings = _LiveSettings()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

PLACEHOLDER_VALUES = {
    "change-me", "your-msg91-auth-key", "your-email@gmail.com",
    "your-app-password", "your-template-id", "change-me-jwt-secret",
    "change-me-to-a-random-64-char-string", "minioadmin",
}


def is_placeholder(value: str) -> bool:
    return not value or value.strip().lower() in PLACEHOLDER_VALUES or value.startswith("change-me")


def _section(title: str):
    print(f"\n{'─' * 55}")
    print(f"  {title}")
    print('─' * 55)


# ─────────────────────────────────────────────────────────────────────────────
# 1. PostgreSQL (NeonDB)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_postgresql_connection():
    """Connect to PostgreSQL and run a simple query."""
    _section("PostgreSQL / NeonDB")
    db_url = settings.DATABASE_URL

    # asyncpg uses a slightly different URL format – strip the +asyncpg driver prefix
    raw_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    print(f"  URL  : {raw_url.split('@')[-1]}")   # hide credentials

    try:
        import asyncpg

        # Parse URL into asyncpg connect kwargs
        # asyncpg.connect() accepts a raw postgres:// DSN
        conn = await asyncio.wait_for(
            asyncpg.connect(raw_url, ssl="require"),
            timeout=15.0,
        )
        version = await conn.fetchval("SELECT version()")
        await conn.close()

        print(f"  ✅  Connected! PostgreSQL: {version[:60]}...")
        assert version, "Expected a non-empty version string"

    except asyncio.TimeoutError:
        pytest.fail("❌  Connection timed out after 15 s")
    except Exception as exc:
        pytest.fail(f"❌  {type(exc).__name__}: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Redis
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_redis_connection():
    """Ping the Redis server."""
    _section("Redis")
    redis_url = settings.REDIS_URL
    print(f"  URL  : {redis_url}")

    if "localhost" in redis_url or "127.0.0.1" in redis_url:
        # Check if port is actually open before trying
        host, port_str = "localhost", "6379"
        try:
            port = int(redis_url.split(":")[-1].split("/")[0])
        except Exception:
            port = 6379
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        open_result = s.connect_ex((host, port))
        s.close()
        if open_result != 0:
            pytest.skip(f"⚠️   Redis not running on {host}:{port} — skipping (expected in dev).")

    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(redis_url, decode_responses=True, socket_connect_timeout=5)
        pong = await r.ping()
        await r.aclose()
        print(f"  ✅  PING → {pong}")
        assert pong is True

    except Exception as exc:
        pytest.fail(f"❌  {type(exc).__name__}: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. India Post API (public — no key needed)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_india_post_api():
    """Look up pin code 110001 (New Delhi) to verify the India Post API is reachable."""
    _section("India Post API")
    url = f"{settings.INDIA_POST_API_URL}/110001"
    print(f"  URL  : {url}")

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url)

    print(f"  HTTP : {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    data = resp.json()
    assert isinstance(data, list) and data, "Expected non-empty list"
    status = data[0].get("Status")
    post_offices = data[0].get("PostOffice", [])
    district = post_offices[0].get("District") if post_offices else "N/A"
    state    = post_offices[0].get("State") if post_offices else "N/A"

    print(f"  ✅  Status={status}, District={district}, State={state}")
    assert status == "Success", f"Expected Status=Success, got {status}"


# ─────────────────────────────────────────────────────────────────────────────
# 4. Data.gov.in API key
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_data_gov_api_key():
    """Fetch 1 record from a agriculture resource to validate the API key."""
    _section("Data.gov.in API")

    api_key = settings.DATA_GOV_API_KEY
    if is_placeholder(api_key):
        pytest.skip("⚠️   DATA_GOV_API_KEY is a placeholder — configure it to test.")

    # Agriculture crop production resource
    resource_id = "9ef84268-d588-465a-a308-a864a43d0070"
    url = f"{settings.DATA_GOV_API_URL}/{resource_id}"
    params = {"api-key": api_key, "format": "json", "limit": 1}
    print(f"  URL  : {url}")

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, params=params)
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        pytest.skip(f"⚠️   data.gov.in not reachable from this network ({exc}). Test on a different network.")

    print(f"  HTTP : {resp.status_code}")

    if resp.status_code == 401 or resp.status_code == 403:
        pytest.fail(f"❌  API key rejected: HTTP {resp.status_code} — {resp.text[:200]}")
    if resp.status_code == 404:
        pytest.skip("⚠️   Resource ID not found on data.gov.in (may have changed).")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}\n{resp.text[:300]}"

    body = resp.json()
    count = body.get("count", body.get("total", "?"))
    records = body.get("records", body.get("data", []))
    print(f"  ✅  API key valid! Total records={count}, got {len(records)} sample record(s)")


# ─────────────────────────────────────────────────────────────────────────────
# 5. PMFBY API reachability
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pmfby_api_reachability():
    """Check if the PMFBY base URL is reachable (government site may be slow)."""
    _section("PMFBY API")
    base_url = settings.PMFBY_API_URL
    print(f"  URL  : {base_url}")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(base_url)
        print(f"  HTTP : {resp.status_code}")
        # Government APIs often return 404/405 on the base path but the host is reachable
        reachable = resp.status_code < 500
        if reachable:
            print(f"  ✅  Host reachable (status {resp.status_code})")
        else:
            print(f"  ⚠️   Host returned 5xx — not configured or unreachable")
        # We don't fail on 4xx: the endpoint exists but may require auth / specific path
        assert resp.status_code != 000, "No response"
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        pytest.skip(f"⚠️   PMFBY API not reachable ({exc}). This is normal — it is a government-only API.")
    except Exception as exc:
        pytest.skip(f"⚠️   PMFBY check failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 6. LGD API reachability
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_lgd_api_reachability():
    """Check if the LGD (Local Government Directory) API base URL is reachable."""
    _section("LGD API")
    lgd_url = settings.LGD_API_URL
    print(f"  URL  : {lgd_url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(lgd_url)
        print(f"  HTTP : {resp.status_code}")
        reachable = resp.status_code < 500
        if reachable:
            print(f"  ✅  Host reachable (status {resp.status_code})")
        else:
            print(f"  ⚠️   Host returned 5xx")
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        pytest.skip(f"⚠️   LGD API not reachable ({exc}). This is normal — it is a government-only API.")
    except Exception as exc:
        pytest.skip(f"⚠️   LGD check failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 7. MSG91 SMS API key
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_msg91_auth_key():
    """Validate MSG91 auth key by calling their /balance endpoint (read-only)."""
    _section("MSG91 SMS")

    auth_key = settings.MSG91_AUTH_KEY
    if is_placeholder(auth_key):
        pytest.skip("⚠️   MSG91_AUTH_KEY is a placeholder — add your real key to test.")

    # MSG91 balance/info endpoint – does not send any SMS
    url = "https://api.msg91.com/api/balance.php"
    params = {"authkey": auth_key, "type": "0"}
    print(f"  URL  : {url}")

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params)

    print(f"  HTTP : {resp.status_code}")
    print(f"  Body : {resp.text[:200]}")

    if resp.status_code == 200 and "error" not in resp.text.lower():
        print("  ✅  MSG91 key is valid and has balance info")
    elif "authentication failed" in resp.text.lower() or "invalid" in resp.text.lower():
        pytest.fail(f"❌  MSG91 key rejected: {resp.text[:200]}")
    else:
        # MSG91 can return other status codes depending on account type
        print(f"  ⚠️   Unexpected response — manually verify the key")

    assert resp.status_code == 200, f"Expected HTTP 200 from MSG91, got {resp.status_code}"


# ─────────────────────────────────────────────────────────────────────────────
# 8. SMTP Email connectivity
# ─────────────────────────────────────────────────────────────────────────────

def test_smtp_connectivity():
    """Check SMTP connection using credentials from .env (does not send email)."""
    _section("SMTP Email")

    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASSWORD
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT

    print(f"  Host : {smtp_host}:{smtp_port}")
    print(f"  User : {smtp_user}")

    if is_placeholder(smtp_user) or is_placeholder(smtp_pass):
        pytest.skip("⚠️   SMTP credentials are placeholders — configure them to test.")

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.quit()
        print(f"  ✅  SMTP login successful as {smtp_user}")
    except smtplib.SMTPAuthenticationError as exc:
        pytest.fail(f"❌  SMTP authentication failed: {exc}")
    except (smtplib.SMTPConnectError, OSError, TimeoutError) as exc:
        pytest.fail(f"❌  Cannot connect to {smtp_host}:{smtp_port} — {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 9. Cloudinary credentials
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cloudinary_credentials():
    """Verify Cloudinary cloud credentials using the usage API (read-only)."""
    _section("Cloudinary")

    cloud_name   = _env.get("cloudinary_cloud_name", "").strip()
    api_key      = _env.get("cloudinary_api_key", "").strip()
    api_secret   = _env.get("cloudinary_api_secret", "").strip()

    if not cloud_name or not api_key or not api_secret:
        pytest.skip("⚠️   Cloudinary credentials not set in .env — skipping.")

    if is_placeholder(api_key) or is_placeholder(api_secret):
        pytest.skip("⚠️   Cloudinary credentials are placeholders — configure them.")

    print(f"  Cloud: {cloud_name}")
    print(f"  Key  : {api_key}")

    # Cloudinary usage endpoint uses HTTP Basic auth (api_key:api_secret)
    credentials = b64encode(f"{api_key}:{api_secret}".encode()).decode()
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/usage"

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, headers={"Authorization": f"Basic {credentials}"})

    print(f"  HTTP : {resp.status_code}")

    if resp.status_code == 401:
        pytest.fail(f"❌  Cloudinary credentials rejected (401): {resp.text[:200]}")
    elif resp.status_code == 403:
        pytest.fail(f"❌  Cloudinary access denied (403): {resp.text[:200]}")
    elif resp.status_code == 200:
        data = resp.json()
        plan = data.get("plan", "Unknown")
        credits_used = data.get("credits", {}).get("used", "?")
        print(f"  ✅  Cloudinary valid! Plan={plan}, Credits used={credits_used}")
    else:
        print(f"  ⚠️   Unexpected status {resp.status_code}: {resp.text[:200]}")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"


# ─────────────────────────────────────────────────────────────────────────────
# 10. SQLAlchemy engine sanity-check (same DB, via ORM layer)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_sqlalchemy_engine():
    """Confirm the ORM async engine can reach the database."""
    _section("SQLAlchemy ORM Engine")
    print(f"  URL  : {settings.DATABASE_URL.split('@')[-1]}")

    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text

        engine = create_async_engine(
            settings.DATABASE_URL,
            connect_args={"ssl": "require"},
            pool_pre_ping=True,
        )
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar()
        await engine.dispose()

        print(f"  ✅  SELECT 1 → {val}")
        assert val == 1

    except Exception as exc:
        pytest.fail(f"❌  {type(exc).__name__}: {exc}")
