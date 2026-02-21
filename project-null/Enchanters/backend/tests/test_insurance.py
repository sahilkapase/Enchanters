"""test_insurance.py — Tests for /api/v1/insurance/* endpoints."""

import uuid
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient

from app.core.exceptions import NotFoundException


PLAN_ID = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")


def _make_plan_mock():
    plan = MagicMock()
    plan.id = PLAN_ID
    plan.name_en = "PMFBY - Pradhan Mantri Fasal Bima Yojana"
    plan.name_hi = "प्रधानमंत्री फसल बीमा योजना"
    plan.plan_type = "pmfby"
    plan.description_en = "Crop insurance scheme"
    plan.description_hi = "फसल बीमा योजना"
    plan.coverage = "Crop loss due to natural calamities"
    plan.premium_info = "2% for Kharif, 1.5% for Rabi"
    plan.eligibility = "All farmers growing notified crops"
    plan.how_to_enroll = "Through bank or CSC"
    plan.is_active = True
    return plan


# ── GET /insurance/plans ──────────────────────────────────────────────────────

class TestListPlans:
    URL = "/api/v1/insurance/plans"

    @pytest.mark.asyncio
    async def test_list_plans_success(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.insurance.insurance_service.list_plans",
            new_callable=AsyncMock,
            return_value=[_make_plan_mock()],
        ):
            resp = await client.get(self.URL, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name_en"] == "PMFBY - Pradhan Mantri Fasal Bima Yojana"
        assert data[0]["is_active"] is True

    @pytest.mark.asyncio
    async def test_list_plans_empty(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.insurance.insurance_service.list_plans",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.get(self.URL, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_plans_unauthenticated(self, unauth_client: AsyncClient):
        resp = await unauth_client.get(self.URL)
        assert resp.status_code == 403


# ── GET /insurance/plans/{id} ─────────────────────────────────────────────────

class TestGetPlan:
    def url(self):
        return f"/api/v1/insurance/plans/{PLAN_ID}"

    @pytest.mark.asyncio
    async def test_get_plan_success(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.insurance.insurance_service.get_plan",
            new_callable=AsyncMock,
            return_value=_make_plan_mock(),
        ):
            resp = await client.get(self.url(), headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["plan_type"] == "pmfby"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_plan_not_found(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.insurance.insurance_service.get_plan",
            new_callable=AsyncMock,
            side_effect=NotFoundException("Insurance Plan"),
        ):
            resp = await client.get(self.url(), headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_plan_invalid_uuid(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/insurance/plans/not-a-uuid", headers=auth_headers)
        assert resp.status_code == 422


# ── POST /insurance/calculate-premium ────────────────────────────────────────

class TestCalculatePremium:
    URL = "/api/v1/insurance/calculate-premium"

    VALID_BODY = {
        "crop": "wheat",
        "season": "rabi",
        "district": "Ahmedabad",
        "land_area": 2.5,
    }

    def _mock_premium_result(self):
        return {
            "crop": "wheat",
            "season": "rabi",
            "district": "Ahmedabad",
            "land_area": 2.5,
            "sum_insured": 50000.0,
            "farmer_premium": 750.0,
            "govt_subsidy": 5250.0,
            "insurance_company": "Agriculture Insurance Company of India",
            "premium_rate_percent": 1.5,
            "source": "local_calculation",
        }

    @pytest.mark.asyncio
    async def test_calculate_premium_success(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.insurance.insurance_service.calculate_premium",
            new_callable=AsyncMock,
            return_value=self._mock_premium_result(),
        ):
            resp = await client.post(self.URL, json=self.VALID_BODY, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["crop"] == "wheat"
        assert data["farmer_premium"] == 750.0
        assert data["source"] == "local_calculation"
        assert "sum_insured" in data

    @pytest.mark.asyncio
    async def test_calculate_premium_kharif(self, client: AsyncClient, auth_headers: dict):
        body = {**self.VALID_BODY, "crop": "rice", "season": "kharif"}
        result = {**self._mock_premium_result(), "crop": "rice", "season": "kharif"}
        with patch(
            "app.api.v1.insurance.insurance_service.calculate_premium",
            new_callable=AsyncMock,
            return_value=result,
        ):
            resp = await client.post(self.URL, json=body, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["season"] == "kharif"

    @pytest.mark.asyncio
    async def test_calculate_premium_missing_crop(self, client: AsyncClient, auth_headers: dict):
        body = {k: v for k, v in self.VALID_BODY.items() if k != "crop"}
        resp = await client.post(self.URL, json=body, headers=auth_headers)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_premium_invalid_season(self, client: AsyncClient, auth_headers: dict):
        body = {**self.VALID_BODY, "season": "winter"}  # not a valid Season
        resp = await client.post(self.URL, json=body, headers=auth_headers)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_premium_zero_land(self, client: AsyncClient, auth_headers: dict):
        body = {**self.VALID_BODY, "land_area": 0}  # must be > 0
        resp = await client.post(self.URL, json=body, headers=auth_headers)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_premium_unauthenticated(self, unauth_client: AsyncClient):
        resp = await unauth_client.post(self.URL, json=self.VALID_BODY)
        assert resp.status_code == 403


# ── POST /insurance/plans/{id}/generate-form ──────────────────────────────────

class TestGenerateInsuranceForm:
    def url(self):
        return f"/api/v1/insurance/plans/{PLAN_ID}/generate-form"

    @pytest.mark.asyncio
    async def test_generate_form_success(self, client: AsyncClient, auth_headers: dict):
        form_mock = {
            "file_key": "forms/KS-MH-2025-001/pmfby.pdf",
            "file_name": "pmfby.pdf",
            "download_url": "https://s3.example.com/forms/pmfby.pdf",
            "message": "Insurance form generated successfully",
        }
        with patch(
            "app.api.v1.insurance.insurance_service.generate_insurance_form",
            new_callable=AsyncMock,
            return_value=form_mock,
        ):
            resp = await client.post(self.url(), headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "file_key" in data
        assert "message" in data

    @pytest.mark.asyncio
    async def test_generate_form_plan_not_found(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.insurance.insurance_service.generate_insurance_form",
            new_callable=AsyncMock,
            side_effect=NotFoundException("Insurance Plan"),
        ):
            resp = await client.post(self.url(), headers=auth_headers)
        assert resp.status_code == 404
