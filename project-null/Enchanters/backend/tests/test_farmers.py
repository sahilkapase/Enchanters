"""test_farmers.py — Tests for /api/v1/farmers/* endpoints."""

import uuid
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient
from datetime import datetime, timezone

from app.core.exceptions import NotFoundException
from tests.conftest import FARMER_UUID, FARMER_KID


def _make_farmer_response():
    return {
        "id": str(FARMER_UUID),
        "farmer_id": FARMER_KID,
        "name": "Raju Test",
        "phone": "9876543210",
        "email": "raju@test.com",
        "email_verified": False,
        "phone_verified": True,
        "pin_code": "380001",
        "district": "Ahmedabad",
        "state": "Gujarat",
        "land_area": 5.0,
        "land_unit": "acre",
        "language_pref": "hi",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "profile": None,
        "crops": [],
        "documents": [],
    }


# ── GET /me ───────────────────────────────────────────────────────────────────

class TestGetMe:
    URL = "/api/v1/farmers/me"

    @pytest.mark.asyncio
    async def test_get_me_success(self, client: AsyncClient, auth_headers: dict):
        mock_farmer = MagicMock()
        mock_farmer.id = FARMER_UUID
        mock_farmer.farmer_id = FARMER_KID
        mock_farmer.name = "Raju Test"
        mock_farmer.phone = "9876543210"
        mock_farmer.email = "raju@test.com"
        mock_farmer.email_verified = False
        mock_farmer.phone_verified = True
        mock_farmer.pin_code = "380001"
        mock_farmer.district = "Ahmedabad"
        mock_farmer.state = "Gujarat"
        mock_farmer.land_area = 5.0
        mock_farmer.land_unit = "acre"
        mock_farmer.language_pref = "hi"
        mock_farmer.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
        mock_farmer.updated_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
        mock_farmer.profile = None
        mock_farmer.crops = []
        mock_farmer.documents = []

        with patch(
            "app.api.v1.farmers.farmer_service.get_farmer_full",
            new_callable=AsyncMock,
            return_value=mock_farmer,
        ):
            resp = await client.get(self.URL, headers=auth_headers)

        assert resp.status_code == 200
        data = resp.json()
        assert data["farmer_id"] == FARMER_KID
        assert data["phone"] == "9876543210"
        assert "crops" in data
        assert "documents" in data

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, unauth_client: AsyncClient):
        resp = await unauth_client.get(self.URL)
        assert resp.status_code == 403


# ── PATCH /me ─────────────────────────────────────────────────────────────────

class TestUpdateMe:
    URL = "/api/v1/farmers/me"

    @pytest.mark.asyncio
    async def test_update_name(self, client: AsyncClient, auth_headers: dict):
        mock_farmer = MagicMock()
        mock_farmer.id = FARMER_UUID
        mock_farmer.farmer_id = FARMER_KID
        mock_farmer.name = "Updated Name"
        mock_farmer.phone = "9876543210"
        mock_farmer.email = None
        mock_farmer.email_verified = False
        mock_farmer.phone_verified = True
        mock_farmer.pin_code = "380001"
        mock_farmer.district = "Ahmedabad"
        mock_farmer.state = "Gujarat"
        mock_farmer.land_area = 5.0
        mock_farmer.land_unit = "acre"
        mock_farmer.language_pref = "hi"
        mock_farmer.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
        mock_farmer.updated_at = datetime(2025, 1, 2, tzinfo=timezone.utc)
        mock_farmer.profile = None
        mock_farmer.crops = []
        mock_farmer.documents = []

        with patch(
            "app.api.v1.farmers.farmer_service.update_farmer",
            new_callable=AsyncMock,
            return_value=mock_farmer,
        ):
            resp = await client.patch(self.URL, json={"name": "Updated Name"}, headers=auth_headers)

        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_invalid_pin_code(self, client: AsyncClient, auth_headers: dict):
        resp = await client.patch(self.URL, json={"pin_code": "abc"}, headers=auth_headers)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_update_invalid_land_area(self, client: AsyncClient, auth_headers: dict):
        resp = await client.patch(self.URL, json={"land_area": -1.0}, headers=auth_headers)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_update_unauthenticated(self, unauth_client: AsyncClient):
        resp = await unauth_client.patch(self.URL, json={"name": "Ghost"})
        assert resp.status_code == 403


# ── PUT /me/profile ───────────────────────────────────────────────────────────

class TestUpsertProfile:
    URL = "/api/v1/farmers/me/profile"

    @pytest.mark.asyncio
    async def test_upsert_profile_success(self, client: AsyncClient, auth_headers: dict):
        profile_mock = MagicMock()
        profile_mock.aadhaar_masked = "1234"
        profile_mock.ration_card_no = None
        profile_mock.bank_ifsc = None
        profile_mock.irrigation_type = "rainfed"
        profile_mock.ownership_type = "owned"

        with patch(
            "app.api.v1.farmers.farmer_service.create_or_update_profile",
            new_callable=AsyncMock,
            return_value=profile_mock,
        ):
            resp = await client.put(
                self.URL,
                json={"irrigation_type": "rainfed", "ownership_type": "owned"},
                headers=auth_headers,
            )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_upsert_profile_invalid_aadhaar(self, client: AsyncClient, auth_headers: dict):
        # aadhaar_masked must be exactly 4 digits
        resp = await client.put(self.URL, json={"aadhaar_masked": "12"}, headers=auth_headers)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_upsert_profile_invalid_ifsc(self, client: AsyncClient, auth_headers: dict):
        resp = await client.put(self.URL, json={"bank_ifsc": "BADIFSC"}, headers=auth_headers)
        assert resp.status_code == 422


# ── GET /me/crops ─────────────────────────────────────────────────────────────

class TestCrops:
    LIST_URL = "/api/v1/farmers/me/crops"
    CROP_ID = uuid.uuid4()

    @pytest.mark.asyncio
    async def test_list_crops_empty(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.farmers.farmer_service.list_crops",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.get(self.LIST_URL, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_crops_with_data(self, client: AsyncClient, auth_headers: dict):
        crop_mock = MagicMock()
        crop_mock.id = self.CROP_ID
        crop_mock.crop_name = "Wheat"
        crop_mock.season = "rabi"
        crop_mock.year = 2025
        crop_mock.is_active = True

        with patch(
            "app.api.v1.farmers.farmer_service.list_crops",
            new_callable=AsyncMock,
            return_value=[crop_mock],
        ):
            resp = await client.get(self.LIST_URL, headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["crop_name"] == "Wheat"

    @pytest.mark.asyncio
    async def test_add_crop_success(self, client: AsyncClient, auth_headers: dict):
        crop_mock = MagicMock()
        crop_mock.id = self.CROP_ID
        crop_mock.crop_name = "Rice"
        crop_mock.season = "kharif"
        crop_mock.year = 2025
        crop_mock.is_active = True

        with patch(
            "app.api.v1.farmers.farmer_service.add_crop",
            new_callable=AsyncMock,
            return_value=crop_mock,
        ):
            resp = await client.post(
                self.LIST_URL,
                json={"crop_name": "Rice", "season": "kharif", "year": 2025},
                headers=auth_headers,
            )
        assert resp.status_code == 201
        assert resp.json()["crop_name"] == "Rice"

    @pytest.mark.asyncio
    async def test_add_crop_invalid_season(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            self.LIST_URL,
            json={"crop_name": "Rice", "season": "monsoon", "year": 2025},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_add_crop_missing_year(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            self.LIST_URL,
            json={"crop_name": "Rice", "season": "kharif"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_remove_crop_success(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.farmers.farmer_service.remove_crop",
            new_callable=AsyncMock,
            return_value={"message": "Crop removed"},
        ):
            resp = await client.delete(
                f"{self.LIST_URL}/{self.CROP_ID}",
                headers=auth_headers,
            )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_crops_unauthenticated(self, unauth_client: AsyncClient):
        resp = await unauth_client.get(self.LIST_URL)
        assert resp.status_code == 403


# ── GET /me/documents ─────────────────────────────────────────────────────────

class TestDocuments:
    LIST_URL = "/api/v1/farmers/me/documents"
    DOC_ID = uuid.uuid4()

    @pytest.mark.asyncio
    async def test_list_documents_empty(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.farmers.farmer_service.list_documents",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.get(self.LIST_URL, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_delete_document_success(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.farmers.farmer_service.delete_document",
            new_callable=AsyncMock,
            return_value={"message": "Document deleted"},
        ):
            resp = await client.delete(
                f"{self.LIST_URL}/{self.DOC_ID}",
                headers=auth_headers,
            )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_document_not_found(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.farmers.farmer_service.delete_document",
            new_callable=AsyncMock,
            side_effect=NotFoundException("Document"),
        ):
            resp = await client.delete(
                f"{self.LIST_URL}/{self.DOC_ID}",
                headers=auth_headers,
            )
        assert resp.status_code == 404


# ── GET /me/access-log ────────────────────────────────────────────────────────

class TestAccessLog:
    URL = "/api/v1/farmers/me/access-log"

    @pytest.mark.asyncio
    async def test_access_log_empty(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.farmers.farmer_service.get_access_log",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.get(self.URL, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []


# ── GET /me/forms ─────────────────────────────────────────────────────────────

class TestForms:
    URL = "/api/v1/farmers/me/forms"

    @pytest.mark.asyncio
    async def test_list_forms_empty(self, client: AsyncClient, auth_headers: dict):
        with patch(
            "app.api.v1.farmers.farmer_service.list_generated_forms",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.get(self.URL, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []
