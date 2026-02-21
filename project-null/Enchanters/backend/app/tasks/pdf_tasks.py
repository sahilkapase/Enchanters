import asyncio
from app.tasks.celery_app import celery_app
from app.database import async_session_factory
from app.core.pdf_builder import build_scheme_form_pdf, build_insurance_form_pdf
from app.services.document_service import upload_bytes_to_s3
import logging

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.pdf_tasks.generate_scheme_pdf")
def generate_scheme_pdf(farmer_data: dict, scheme_data: dict, file_key: str, form_id: str):
    """Background task to generate scheme application PDF and upload to S3."""
    try:
        pdf_bytes, filename = build_scheme_form_pdf(farmer_data, scheme_data)
        _run_async(upload_bytes_to_s3(pdf_bytes, file_key, "application/pdf"))
        logger.info("Background PDF generated: %s (%d bytes)", file_key, len(pdf_bytes))
        return {"file_key": file_key, "file_name": filename, "size": len(pdf_bytes)}
    except Exception as e:
        logger.error("PDF generation failed for %s: %s", file_key, str(e))
        raise


@celery_app.task(name="app.tasks.pdf_tasks.generate_insurance_pdf")
def generate_insurance_pdf(farmer_data: dict, plan_data: dict, file_key: str):
    """Background task to generate insurance form PDF."""
    try:
        pdf_bytes, filename = build_insurance_form_pdf(farmer_data, plan_data)
        _run_async(upload_bytes_to_s3(pdf_bytes, file_key, "application/pdf"))
        logger.info("Background insurance PDF generated: %s", file_key)
        return {"file_key": file_key, "file_name": filename, "size": len(pdf_bytes)}
    except Exception as e:
        logger.error("Insurance PDF generation failed: %s", str(e))
        raise


@celery_app.task(name="app.tasks.pdf_tasks.batch_generate_forms")
def batch_generate_forms(farmer_ids: list[str]):
    """Generate forms for multiple farmers (e.g., for CSC agent bulk requests)."""
    results = []
    for fid in farmer_ids:
        try:
            logger.info("Batch form generation for farmer %s", fid)
            results.append({"farmer_id": fid, "status": "queued"})
        except Exception as e:
            results.append({"farmer_id": fid, "status": "failed", "error": str(e)})
    return results
