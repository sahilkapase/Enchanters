"""test_location.py — Tests for /api/v1/location/* endpoints.

Location endpoints are public (no auth required) and call external services
which are mocked here.
"""

import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient


# ── GET /location/pin/{pincode} ───────────────────────────────────────────────

class TestPinLookup:
    def url(self, pincode: str):
        return f"/api/v1/location/pin/{pincode}"

    @pytest.mark.asyncio
    async def test_pin_lookup_success(self, client: AsyncClient):
        pin_data = {
            "pincode": "380001",
            "district": "Ahmedabad",
            "state": "Gujarat",
            "country": "India",
            "post_offices": [
                {
                    "name": "Ahmedabad GPO",
                    "branch_type": "Head Post Office",
                    "delivery_status": "Delivery",
                    "division": "Ahmedabad City",
                    "region": "Ahmedabad",
                    "block": "Ahmedabad",
                }
            ],
        }
        with patch(
            "app.services.location_service.lookup_pincode",
            new_callable=AsyncMock,
            return_value=pin_data,
        ):
            resp = await client.get(self.url("380001"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["district"] == "Ahmedabad"
        assert data["state"] == "Gujarat"
        assert data["pincode"] == "380001"
        assert isinstance(data["post_offices"], list)

    @pytest.mark.asyncio
    async def test_pin_lookup_rural_pincode(self, client: AsyncClient):
        pin_data = {
            "pincode": "413501",
            "district": "Solapur",
            "state": "Maharashtra",
            "country": "India",
            "post_offices": [],
        }
        with patch(
            "app.services.location_service.lookup_pincode",
            new_callable=AsyncMock,
            return_value=pin_data,
        ):
            resp = await client.get(self.url("413501"))
        assert resp.status_code == 200
        assert resp.json()["state"] == "Maharashtra"

    @pytest.mark.asyncio
    async def test_pin_lookup_fallback_on_api_failure(self, client: AsyncClient):
        """Confirms the fallback / partial data is still returned (not 500)."""
        fallback = {"pincode": "999999", "district": "", "state": "", "country": "India", "post_offices": []}
        with patch(
            "app.services.location_service.lookup_pincode",
            new_callable=AsyncMock,
            return_value=fallback,
        ):
            resp = await client.get(self.url("999999"))
        assert resp.status_code == 200


# ── GET /location/states ──────────────────────────────────────────────────────

class TestListStates:
    URL = "/api/v1/location/states"

    @pytest.mark.asyncio
    async def test_list_states_success(self, client: AsyncClient):
        sample_states = [
            "Gujarat", "Maharashtra", "Rajasthan", "Uttar Pradesh", "Punjab"
        ]
        with patch(
            "app.services.location_service.list_states",
            return_value=sample_states,
        ):
            resp = await client.get(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert "states" in data
        assert isinstance(data["states"], list)
        assert "Gujarat" in data["states"]

    @pytest.mark.asyncio
    async def test_list_states_not_empty(self, client: AsyncClient):
        """Real list_states() uses INDIAN_STATES constant — it should never be empty."""
        with patch(
            "app.services.location_service.list_states",
            return_value=["Andhra Pradesh", "Gujarat"],
        ):
            resp = await client.get(self.URL)
        data = resp.json()
        assert len(data["states"]) > 0


# ── GET /location/districts/{state} ──────────────────────────────────────────

class TestListDistricts:
    def url(self, state: str):
        return f"/api/v1/location/districts/{state}"

    @pytest.mark.asyncio
    async def test_list_districts_gujarat(self, client: AsyncClient):
        gujaratdistricts = ["Ahmedabad", "Surat", "Vadodara", "Rajkot"]
        with patch(
            "app.services.location_service.list_districts",
            new_callable=AsyncMock,
            return_value=gujaratdistricts,
        ):
            resp = await client.get(self.url("Gujarat"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["state"] == "Gujarat"
        assert "districts" in data
        assert "Ahmedabad" in data["districts"]

    @pytest.mark.asyncio
    async def test_list_districts_unknown_state(self, client: AsyncClient):
        with patch(
            "app.services.location_service.list_districts",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.get(self.url("Narnia"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["state"] == "Narnia"
        assert data["districts"] == []

    @pytest.mark.asyncio
    async def test_list_districts_maharashtra(self, client: AsyncClient):
        mh_districts = ["Pune", "Mumbai City", "Nagpur", "Nashik"]
        with patch(
            "app.services.location_service.list_districts",
            new_callable=AsyncMock,
            return_value=mh_districts,
        ):
            resp = await client.get(self.url("Maharashtra"))
        assert resp.status_code == 200
        data = resp.json()
        assert "Pune" in data["districts"]
