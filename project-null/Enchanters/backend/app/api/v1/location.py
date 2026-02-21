from fastapi import APIRouter
from app.services import location_service

router = APIRouter(prefix="/location", tags=["Location"])


@router.get("/pin/{pincode}")
async def pin_lookup(pincode: str):
    return await location_service.get_pin_details(pincode)


@router.get("/states")
async def list_states():
    return {"states": location_service.list_states()}


@router.get("/districts/{state}")
async def list_districts(state: str):
    districts = await location_service.list_districts(state)
    return {"state": state, "districts": districts}
