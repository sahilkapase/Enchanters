import uuid
import os
from io import BytesIO
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.farmer import FarmerDocument
from app.core.constants import ALLOWED_DOC_EXTENSIONS, MAX_FILE_SIZE_BYTES, DocType
from app.core.exceptions import InvalidFileException
from app.config import settings
import boto3
from botocore.config import Config as BotoConfig
import logging

logger = logging.getLogger(__name__)


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
        config=BotoConfig(signature_version="s3v4"),
    )


def _validate_file(file: UploadFile) -> str:
    if not file.filename:
        raise InvalidFileException("File must have a name")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_DOC_EXTENSIONS:
        raise InvalidFileException(f"File type '{ext}' not allowed. Allowed: {', '.join(ALLOWED_DOC_EXTENSIONS)}")

    return ext


async def upload_document(
    db: AsyncSession,
    farmer_id: uuid.UUID,
    farmer_kid: str,
    doc_type: DocType,
    file: UploadFile,
) -> FarmerDocument:
    ext = _validate_file(file)

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise InvalidFileException(f"File too large. Maximum size: {MAX_FILE_SIZE_BYTES // (1024*1024)}MB")

    file_uuid = uuid.uuid4()
    file_key = f"documents/{farmer_kid}/{doc_type.value}/{file_uuid}{ext}"

    try:
        s3 = _get_s3_client()
        s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=file_key,
            Body=content,
            ContentType=file.content_type or "application/octet-stream",
        )
        logger.info("Uploaded document to S3: %s", file_key)
    except Exception as e:
        logger.error("S3 upload failed: %s", str(e))
        raise InvalidFileException("File upload failed. Please try again.")

    doc = FarmerDocument(
        farmer_id=farmer_id,
        doc_type=doc_type,
        file_key=file_key,
        file_name=file.filename,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)

    return doc


async def upload_bytes_to_s3(data: bytes, file_key: str, content_type: str = "application/pdf") -> str:
    try:
        s3 = _get_s3_client()
        s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=file_key,
            Body=data,
            ContentType=content_type,
        )
        logger.info("Uploaded bytes to S3: %s (%d bytes)", file_key, len(data))
        return file_key
    except Exception as e:
        logger.error("S3 upload failed for %s: %s", file_key, str(e))
        raise InvalidFileException("File upload failed")


def generate_presigned_url(file_key: str, expiration: int = 3600) -> str:
    try:
        s3 = _get_s3_client()
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": file_key},
            ExpiresIn=expiration,
        )
        return url
    except Exception as e:
        logger.error("Failed to generate presigned URL for %s: %s", file_key, str(e))
        return ""
