from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.farmers import router as farmers_router
from app.api.v1.schemes import router as schemes_router
from app.api.v1.insurance import router as insurance_router
from app.api.v1.subsidies import router as subsidies_router
from app.api.v1.location import router as location_router
from app.api.v1.service import router as service_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(farmers_router)
api_v1_router.include_router(schemes_router)
api_v1_router.include_router(insurance_router)
api_v1_router.include_router(subsidies_router)
api_v1_router.include_router(location_router)
api_v1_router.include_router(service_router)
