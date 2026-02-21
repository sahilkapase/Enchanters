"""test_schemes.py — Tests for /api/v1/schemes/* endpoints."""

import uuid
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient
from datetime import date

from app.core.exceptions import NotFoundException, BadRequestException
from tests.conftest import FARMER_UUID


SCHEME_ID = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")


def _make_scheme_list_item(scheme_id=None):
    return {
        "id": str(scheme_id or SCHEME_ID),
        "name_en": "PM-KISAN",
        "name_hi": "पीएम किसान",
        "ministry": "Agriculture",
        "benefit_type": "cash",
        "benefit_amount": "₹6000/year",
        "is_active": True,
        "eligibility_status": "eligible",
        "match_score": 1.0,
        "matched_rules": [],
        "unmatched_rules": [],
    }


def _make_scheme_detail(scheme_id=None):
    item = _make_scheme_list_item(scheme_id)
    return {
        **item,
        "description_en": "Direct income transfer to farmers",
        "description_hi": "किसानों को प्रत्यक्ष आय हस्तांतरण",
        "apply_url": "https://pmkisan.gov.in",
        "documents_required": ["Aadhaar", "Land record"],
        "how_to_apply": "Apply online at pmkisan.gov.in",
        "source_url": "https://pmkisan.gov.in",
        "eligibility_rules": [],
        "deadlines": [],
    }


# ── GET /schemes ──────────────────────────────────────────────────────────────

class TestListSchemes:
    URL = "/api/v1/schemes"

    @pytest.mark.asyncio
    async def test_list_schemes_success(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.schemes.scheme_service.list_schemes_with_eligibility",
            new_callable=AsyncMock,
            return_value=[_make_scheme_list_item()],
        ):
            resp = await client.get(self.URL, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name_en"] == "PM-KISAN"

    @pytest.mark.asyncio
    async def test_list_schemes_empty(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.schemes.scheme_service.list_schemes_with_eligibility",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.get(self.URL, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_schemes_with_crop_filter(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.schemes.scheme_service.list_schemes_with_eligibility",
            new_callable=AsyncMock,
            return_value=[_make_scheme_list_item()],
        ) as mock_svc:
            resp = await client.get(self.URL + "?crop=wheat", headers=auth_headers)
        assert resp.status_code == 200
        mock_svc.assert_called_once()
        call_kwargs = mock_svc.call_args.kwargs
        assert call_kwargs.get("crop") == "wheat"

    @pytest.mark.asyncio
    async def test_list_schemes_with_season_filter(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.schemes.scheme_service.list_schemes_with_eligibility",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_svc:
            resp = await client.get(self.URL + "?season=kharif", headers=auth_headers)
        assert resp.status_code == 200
        call_kwargs = mock_svc.call_args.kwargs
        assert call_kwargs.get("season") == "kharif"

    @pytest.mark.asyncio
    async def test_list_schemes_unauthenticated(self, unauth_client: AsyncClient):
        resp = await unauth_client.get(self.URL)
        assert resp.status_code == 403


# ── GET /schemes/{id} ─────────────────────────────────────────────────────────

class TestGetScheme:
    def url(self):
        return f"/api/v1/schemes/{SCHEME_ID}"

    @pytest.mark.asyncio
    async def test_get_scheme_success(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.schemes.scheme_service.get_scheme_detail",
            new_callable=AsyncMock,
            return_value=_make_scheme_detail(),
        ):
            resp = await client.get(self.url(), headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name_en"] == "PM-KISAN"
        assert "eligibility_rules" in data

    @pytest.mark.asyncio
    async def test_get_scheme_not_found(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.schemes.scheme_service.get_scheme_detail",
            new_callable=AsyncMock,
            side_effect=NotFoundException("Scheme"),
        ):
            resp = await client.get(self.url(), headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_scheme_invalid_uuid(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/schemes/not-a-uuid", headers=auth_headers)
        assert resp.status_code == 422


# ── GET /schemes/{id}/eligibility ─────────────────────────────────────────────

class TestEligibility:
    def url(self):
        return f"/api/v1/schemes/{SCHEME_ID}/eligibility"

    @pytest.mark.asyncio
    async def test_eligibility_success(self, client: AsyncClient, auth_headers: dict):
        elig_mock = {
            "scheme_id": str(SCHEME_ID),
            "scheme_name": "PM-KISAN",
            "status": "eligible",
            "score": 1.0,
            "total_rules": 2,
            "mandatory_rules": 1,
            "matched_mandatory": 1,
            "matched_rules": [],
            "unmatched_rules": [],
        }
        with patch(
            "app.api.v1.schemes.scheme_service.get_eligibility_breakdown",
            new_callable=AsyncMock,
            return_value=elig_mock,
        ):
            resp = await client.get(self.url(), headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data

    @pytest.mark.asyncio
    async def test_eligibility_scheme_not_found(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.schemes.scheme_service.get_eligibility_breakdown",
            new_callable=AsyncMock,
            side_effect=NotFoundException("Scheme"),
        ):
            resp = await client.get(self.url(), headers=auth_headers)
        assert resp.status_code == 404


# ── POST /schemes/{id}/generate-form ─────────────────────────────────────────

class TestGenerateForm:
    def url(self):
        return f"/api/v1/schemes/{SCHEME_ID}/generate-form"

    @pytest.mark.asyncio
    async def test_generate_form_success(self, client: AsyncClient, auth_headers: dict):
        form_id = uuid.uuid4()
        form_mock = {
            "file_key": "forms/KS-MH-2025-001/pm-kisan.pdf",
            "file_name": "pm-kisan.pdf",
            "download_url": "https://s3.example.com/forms/pm-kisan.pdf",
            "message": "Form generated successfully",
        }
        with patch(
            "app.api.v1.schemes.scheme_service.generate_scheme_form",
            new_callable=AsyncMock,
            return_value=form_mock,
        ):
            resp = await client.post(self.url(), headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "file_key" in data
        assert "message" in data

    @pytest.mark.asyncio
    async def test_generate_form_scheme_not_found(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.schemes.scheme_service.generate_scheme_form",
            new_callable=AsyncMock,
            side_effect=NotFoundException("Scheme"),
        ):
            resp = await client.post(self.url(), headers=auth_headers)
        assert resp.status_code == 404


# ── POST /schemes/{id}/remind ─────────────────────────────────────────────────

class TestReminder:
    def url(self):
        return f"/api/v1/schemes/{SCHEME_ID}/remind"

    @pytest.mark.asyncio
    async def test_set_reminder_success(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.schemes.scheme_service.create_scheme_reminder",
            new_callable=AsyncMock,
            return_value={"message": "Reminder set", "reminder_id": str(uuid.uuid4())},
        ):
            resp = await client.post(
                self.url(),
                json={"channel": "sms"},
                headers=auth_headers,
            )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_set_reminder_invalid_channel(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            self.url(),
            json={"channel": "telegram"},    # invalid
            headers=auth_headers,
        )
        assert resp.status_code == 422
