"""test_auth.py — Tests for /api/v1/auth/* endpoints."""

import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient

from app.core.exceptions import ConflictException, NotFoundException, BadRequestException
from tests.conftest import make_farmer_token, FARMER_UUID, FARMER_KID


# ── /signup ───────────────────────────────────────────────────────────────────

class TestSignup:
    BASE = "/api/v1/auth/signup"

    VALID_BODY = {
        "name": "Raju Kumar",
        "phone": "9876543210",
        "pin_code": "380001",
        "land_area": 3.5,
        "land_unit": "acre",
    }

    @pytest.mark.asyncio
    async def test_signup_success(self, client: AsyncClient):
        with patch(
            "app.api.v1.auth.auth_service.signup_farmer",
            new_callable=AsyncMock,
            return_value={"message": "Signup successful. OTP sent to your phone.", "farmer_id": "KS-GJ-2025-001"},
        ):
            resp = await client.post(self.BASE, json=self.VALID_BODY)
        assert resp.status_code == 200
        data = resp.json()
        assert "farmer_id" in data
        assert "message" in data

    @pytest.mark.asyncio
    async def test_signup_with_email(self, client: AsyncClient):
        body = {**self.VALID_BODY, "email": "raju@example.com"}
        with patch(
            "app.api.v1.auth.auth_service.signup_farmer",
            new_callable=AsyncMock,
            return_value={"message": "Signup successful. OTP sent to your phone.", "farmer_id": "KS-GJ-2025-002"},
        ):
            resp = await client.post(self.BASE, json=body)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_signup_invalid_phone_too_short(self, client: AsyncClient):
        body = {**self.VALID_BODY, "phone": "12345"}
        resp = await client.post(self.BASE, json=body)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_signup_invalid_phone_bad_prefix(self, client: AsyncClient):
        # Indian phones must start with 6-9
        body = {**self.VALID_BODY, "phone": "1234567890"}
        resp = await client.post(self.BASE, json=body)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_signup_invalid_pincode(self, client: AsyncClient):
        body = {**self.VALID_BODY, "pin_code": "123"}  # must be 6 digits
        resp = await client.post(self.BASE, json=body)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_signup_zero_land_area(self, client: AsyncClient):
        body = {**self.VALID_BODY, "land_area": 0}  # must be > 0
        resp = await client.post(self.BASE, json=body)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_signup_missing_name(self, client: AsyncClient):
        body = {k: v for k, v in self.VALID_BODY.items() if k != "name"}
        resp = await client.post(self.BASE, json=body)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_signup_duplicate_phone(self, client: AsyncClient):
        with patch(
            "app.api.v1.auth.auth_service.signup_farmer",
            new_callable=AsyncMock,
            side_effect=ConflictException("A farmer with this phone number already exists"),
        ):
            resp = await client.post(self.BASE, json=self.VALID_BODY)
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_signup_name_too_short(self, client: AsyncClient):
        body = {**self.VALID_BODY, "name": "A"}  # min_length=2
        resp = await client.post(self.BASE, json=body)
        assert resp.status_code == 422


# ── /verify-otp ───────────────────────────────────────────────────────────────

class TestVerifyOTP:
    BASE = "/api/v1/auth/verify-otp"

    VALID_BODY = {"phone": "9876543210", "otp": "123456", "type": "phone"}

    @pytest.mark.asyncio
    async def test_verify_otp_success(self, client: AsyncClient):
        with patch(
            "app.api.v1.auth.auth_service.verify_farmer_otp",
            new_callable=AsyncMock,
            return_value={"verified": True},
        ):
            resp = await client.post(self.BASE, json=self.VALID_BODY)
        assert resp.status_code == 200
        assert resp.json()["verified"] is True

    @pytest.mark.asyncio
    async def test_verify_otp_invalid_otp_format(self, client: AsyncClient):
        body = {**self.VALID_BODY, "otp": "12345"}  # must be 6 digits
        resp = await client.post(self.BASE, json=body)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_verify_otp_non_numeric_otp(self, client: AsyncClient):
        body = {**self.VALID_BODY, "otp": "abcdef"}
        resp = await client.post(self.BASE, json=body)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_verify_otp_invalid_type(self, client: AsyncClient):
        body = {**self.VALID_BODY, "type": "sms"}  # only phone/email allowed
        resp = await client.post(self.BASE, json=body)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_verify_otp_wrong_code(self, client: AsyncClient):
        with patch(
            "app.api.v1.auth.auth_service.verify_farmer_otp",
            new_callable=AsyncMock,
            side_effect=BadRequestException("OTP has expired or is invalid"),
        ):
            resp = await client.post(self.BASE, json=self.VALID_BODY)
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_verify_otp_email_type(self, client: AsyncClient):
        body = {**self.VALID_BODY, "type": "email"}
        with patch(
            "app.api.v1.auth.auth_service.verify_farmer_otp",
            new_callable=AsyncMock,
            return_value={"verified": True},
        ):
            resp = await client.post(self.BASE, json=body)
        assert resp.status_code == 200


# ── /login ────────────────────────────────────────────────────────────────────

class TestLogin:
    BASE = "/api/v1/auth/login"

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        with patch(
            "app.api.v1.auth.auth_service.login_farmer",
            new_callable=AsyncMock,
            return_value={"message": "OTP sent to your phone"},
        ):
            resp = await client.post(self.BASE, json={"phone": "9876543210"})
        assert resp.status_code == 200
        assert "message" in resp.json()

    @pytest.mark.asyncio
    async def test_login_invalid_phone(self, client: AsyncClient):
        resp = await client.post(self.BASE, json={"phone": "1234"})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_login_missing_phone(self, client: AsyncClient):
        resp = await client.post(self.BASE, json={})
        assert resp.status_code == 422


# ── /login/verify ─────────────────────────────────────────────────────────────

class TestLoginVerify:
    BASE = "/api/v1/auth/login/verify"

    VALID_BODY = {"phone": "9876543210", "otp": "654321"}

    @pytest.mark.asyncio
    async def test_login_verify_success(self, client: AsyncClient):
        with patch(
            "app.api.v1.auth.auth_service.verify_login",
            new_callable=AsyncMock,
            return_value={
                "access_token": "acc.tok.en",
                "refresh_token": "ref.tok.en",
                "token_type": "bearer",
                "farmer_id": FARMER_KID,
            },
        ):
            resp = await client.post(self.BASE, json=self.VALID_BODY)
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_verify_wrong_otp(self, client: AsyncClient):
        with patch(
            "app.api.v1.auth.auth_service.verify_login",
            new_callable=AsyncMock,
            side_effect=BadRequestException("OTP has expired or is invalid"),
        ):
            resp = await client.post(self.BASE, json=self.VALID_BODY)
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_login_verify_farmer_not_found(self, client: AsyncClient):
        with patch(
            "app.api.v1.auth.auth_service.verify_login",
            new_callable=AsyncMock,
            side_effect=NotFoundException("Farmer"),
        ):
            resp = await client.post(self.BASE, json=self.VALID_BODY)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_login_verify_invalid_otp_format(self, client: AsyncClient):
        body = {**self.VALID_BODY, "otp": "12345"}  # must be 6 digits
        resp = await client.post(self.BASE, json=body)
        assert resp.status_code == 422


# ── /refresh ──────────────────────────────────────────────────────────────────

class TestRefresh:
    BASE = "/api/v1/auth/refresh"

    @pytest.mark.asyncio
    async def test_refresh_success(self, client: AsyncClient):
        with patch(
            "app.api.v1.auth.auth_service.refresh_tokens",
            new_callable=AsyncMock,
            return_value={
                "access_token": "new.acc.token",
                "refresh_token": "new.ref.token",
                "token_type": "bearer",
                "farmer_id": FARMER_KID,
            },
        ):
            resp = await client.post(self.BASE, json={"refresh_token": "some.valid.refresh"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    @pytest.mark.asyncio
    async def test_refresh_missing_token(self, client: AsyncClient):
        resp = await client.post(self.BASE, json={})
        assert resp.status_code == 422


# ── /logout ───────────────────────────────────────────────────────────────────

class TestLogout:
    BASE = "/api/v1/auth/logout"

    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.auth.auth_service.logout_farmer",
            new_callable=AsyncMock,
            return_value={"message": "Logged out successfully"},
        ):
            resp = await client.post(self.BASE, headers=auth_headers)
        assert resp.status_code == 200
        assert "message" in resp.json()

    @pytest.mark.asyncio
    async def test_logout_unauthenticated(self, unauth_client: AsyncClient):
        resp = await unauth_client.post(self.BASE)
        assert resp.status_code == 403
