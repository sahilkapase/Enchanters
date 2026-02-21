from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_farmer
from app.schemas.farmer import (
    FarmerResponse, FarmerUpdate, FarmerProfileCreate, FarmerProfileResponse,
    FarmerCropCreate, FarmerCropResponse, FarmerDocumentResponse,
    AccessLogEntry, GeneratedFormResponse,
)
from app.services import farmer_service
from app.services.document_service import upload_document
from app.models.farmer import Farmer
from app.core.constants import DocType

router = APIRouter(prefix="/farmers", tags=["Farmers"])


@router.get("/me", response_model=FarmerResponse)
async def get_me(
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    full = await farmer_service.get_farmer_full(db, farmer.id)
    return full


@router.patch("/me", response_model=FarmerResponse)
async def update_me(
    body: FarmerUpdate,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    data = body.model_dump(exclude_none=True)
    if "land_unit" in data and data["land_unit"]:
        data["land_unit"] = data["land_unit"].value if hasattr(data["land_unit"], 'value') else data["land_unit"]
    updated = await farmer_service.update_farmer(db, farmer.id, data)
    return updated


@router.put("/me/profile", response_model=FarmerProfileResponse)
async def upsert_profile(
    body: FarmerProfileCreate,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    data = body.model_dump(exclude_none=True)
    if "irrigation_type" in data and data["irrigation_type"]:
        data["irrigation_type"] = data["irrigation_type"].value if hasattr(data["irrigation_type"], 'value') else data["irrigation_type"]
    if "ownership_type" in data and data["ownership_type"]:
        data["ownership_type"] = data["ownership_type"].value if hasattr(data["ownership_type"], 'value') else data["ownership_type"]
    profile = await farmer_service.create_or_update_profile(db, farmer.id, data)
    return profile


@router.get("/me/crops", response_model=list[FarmerCropResponse])
async def list_crops(
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await farmer_service.list_crops(db, farmer.id)


@router.post("/me/crops", response_model=FarmerCropResponse, status_code=201)
async def add_crop(
    body: FarmerCropCreate,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await farmer_service.add_crop(db, farmer.id, body.crop_name, body.season.value, body.year)


@router.delete("/me/crops/{crop_id}")
async def remove_crop(
    crop_id: UUID,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await farmer_service.remove_crop(db, farmer.id, crop_id)


@router.post("/me/documents", response_model=FarmerDocumentResponse, status_code=201)
async def upload_doc(
    doc_type: DocType = Form(...),
    file: UploadFile = File(...),
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    doc = await upload_document(db, farmer.id, farmer.farmer_id, doc_type, file)
    return doc


@router.get("/me/documents", response_model=list[FarmerDocumentResponse])
async def list_docs(
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await farmer_service.list_documents(db, farmer.id)


@router.delete("/me/documents/{doc_id}")
async def delete_doc(
    doc_id: UUID,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await farmer_service.delete_document(db, farmer.id, doc_id)


@router.get("/me/access-log", response_model=list[AccessLogEntry])
async def access_log(
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await farmer_service.get_access_log(db, farmer.id)


@router.get("/me/forms", response_model=list[GeneratedFormResponse])
async def list_forms(
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    return await farmer_service.list_generated_forms(db, farmer.id)
