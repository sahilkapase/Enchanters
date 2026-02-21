"""test_subsidies.py — Tests for /api/v1/subsidies/* endpoints."""

import uuid
import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from datetime import date

from app.core.exceptions import NotFoundException


SUBSIDY_ID = uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")


def _make_subsidy_list_item(subsidy_id=None):
    return {
        "id": str(subsidy_id or SUBSIDY_ID),
        "name_en": "Soil Health Card Scheme",
        "name_hi": "मृदा स्वास्थ्य कार्ड योजना",
        "category": "fertilizer",
        "benefit_amount": "Free soil testing",
        "open_date": str(date(2025, 1, 1)),
        "close_date": str(date(2025, 12, 31)),
        "state": None,
        "is_active": True,
        "status": "open",
    }


def _make_subsidy_detail(subsidy_id=None):
    base = _make_subsidy_list_item(subsidy_id)
    return {
        **base,
        "description_en": "Free soil testing for farmers",
        "description_hi": "किसानों के लिए नि:शुल्क मिट्टी परीक्षण",
        "eligibility": {"land": "all"},
    }


# ── GET /subsidies ────────────────────────────────────────────────────────────

class TestListSubsidies:
    URL = "/api/v1/subsidies"

    @pytest.mark.asyncio
    async def test_list_subsidies_success(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.subsidies.subsidy_service.list_subsidies",
            new_callable=AsyncMock,
            return_value=[_make_subsidy_list_item()],
        ):
            resp = await client.get(self.URL, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name_en"] == "Soil Health Card Scheme"
        assert data[0]["status"] == "open"

    @pytest.mark.asyncio
    async def test_list_subsidies_empty(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.subsidies.subsidy_service.list_subsidies",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.get(self.URL, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_subsidies_with_category_filter(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.subsidies.subsidy_service.list_subsidies",
            new_callable=AsyncMock,
            return_value=[_make_subsidy_list_item()],
        ) as mock_svc:
            resp = await client.get(self.URL + "?category=fertilizer", headers=auth_headers)
        assert resp.status_code == 200
        mock_svc.assert_called_once()
        call_kwargs = mock_svc.call_args.kwargs
        assert call_kwargs.get("category") == "fertilizer"

    @pytest.mark.asyncio
    async def test_list_subsidies_with_state_filter(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.subsidies.subsidy_service.list_subsidies",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_svc:
            resp = await client.get(self.URL + "?state=Gujarat", headers=auth_headers)
        assert resp.status_code == 200
        call_kwargs = mock_svc.call_args.kwargs
        assert call_kwargs.get("state") == "Gujarat"

    @pytest.mark.asyncio
    async def test_list_subsidies_with_status_filter(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.subsidies.subsidy_service.list_subsidies",
            new_callable=AsyncMock,
            return_value=[_make_subsidy_list_item()],
        ) as mock_svc:
            resp = await client.get(self.URL + "?status=open", headers=auth_headers)
        assert resp.status_code == 200
        call_kwargs = mock_svc.call_args.kwargs
        assert call_kwargs.get("status_filter") == "open"

    @pytest.mark.asyncio
    async def test_list_subsidies_unauthenticated(self, unauth_client: AsyncClient):
        resp = await unauth_client.get(self.URL)
        assert resp.status_code == 403


# ── GET /subsidies/calendar ───────────────────────────────────────────────────

class TestSubsidyCalendar:
    URL = "/api/v1/subsidies/calendar"

    @pytest.mark.asyncio
    async def test_calendar_success(self, client: AsyncClient, auth_headers: dict):
        calendar_item = {
            "id": str(SUBSIDY_ID),
            "name_en": "Soil Health Card Scheme",
            "category": "fertilizer",
            "open_date": str(date(2025, 3, 1)),
            "close_date": str(date(2025, 3, 31)),
            "state": None,
            "status": "open",
        }
        with patch(
            "app.api.v1.subsidies.subsidy_service.get_calendar",
            new_callable=AsyncMock,
            return_value=[calendar_item],
        ):
            resp = await client.get(
                self.URL,
                params={"month": 3, "year": 2025},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert data[0]["name_en"] == "Soil Health Card Scheme"

    @pytest.mark.asyncio
    async def test_calendar_missing_params(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get(self.URL, headers=auth_headers)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_calendar_invalid_month(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get(
            self.URL,
            params={"month": 13, "year": 2025},  # month must be 1..12
            headers=auth_headers,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_calendar_invalid_year(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get(
            self.URL,
            params={"month": 3, "year": 1999},   # year must be >= 2020
            headers=auth_headers,
        )
        assert resp.status_code == 422


# ── GET /subsidies/{id} ───────────────────────────────────────────────────────

class TestGetSubsidy:
    def url(self):
        return f"/api/v1/subsidies/{SUBSIDY_ID}"

    @pytest.mark.asyncio
    async def test_get_subsidy_success(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.subsidies.subsidy_service.get_subsidy",
            new_callable=AsyncMock,
            return_value=_make_subsidy_detail(),
        ):
            resp = await client.get(self.url(), headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name_en"] == "Soil Health Card Scheme"
        assert "description_en" in data

    @pytest.mark.asyncio
    async def test_get_subsidy_not_found(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.subsidies.subsidy_service.get_subsidy",
            new_callable=AsyncMock,
            side_effect=NotFoundException("Subsidy"),
        ):
            resp = await client.get(self.url(), headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_subsidy_invalid_uuid(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/subsidies/not-a-uuid", headers=auth_headers)
        assert resp.status_code == 422


# ── POST /subsidies/{id}/remind ───────────────────────────────────────────────

class TestSubsidyReminder:
    def url(self):
        return f"/api/v1/subsidies/{SUBSIDY_ID}/remind"

    @pytest.mark.asyncio
    async def test_set_reminder_sms(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.subsidies.subsidy_service.create_subsidy_reminder",
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
    async def test_set_reminder_whatsapp(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.subsidies.subsidy_service.create_subsidy_reminder",
            new_callable=AsyncMock,
            return_value={"message": "Reminder set"},
        ):
            resp = await client.post(
                self.url(),
                json={"channel": "whatsapp"},
                headers=auth_headers,
            )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_set_reminder_email(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.subsidies.subsidy_service.create_subsidy_reminder",
            new_callable=AsyncMock,
            return_value={"message": "Reminder set"},
        ):
            resp = await client.post(
                self.url(),
                json={"channel": "email"},
                headers=auth_headers,
            )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_set_reminder_invalid_channel(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            self.url(),
            json={"channel": "push_notification"},  # invalid
            headers=auth_headers,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_set_reminder_subsidy_not_found(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.subsidies.subsidy_service.create_subsidy_reminder",
            new_callable=AsyncMock,
            side_effect=NotFoundException("Subsidy"),
        ):
            resp = await client.post(
                self.url(),
                json={"channel": "sms"},
                headers=auth_headers,
            )
        assert resp.status_code == 404
