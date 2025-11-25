import os
import uuid
import time
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
from typing import Optional
from tasks import ocr_task
from config import settings
from utils.storage import save_upload_file, load_result_json, list_job_status
from utils.audit import append_audit
from ocr.tesseract_pipeline import TesseractPipeline
import json

router = APIRouter()

@router.post("/extract")
async def extract(file: UploadFile = File(...), sync: Optional[bool] = Query(False)):
    # accept image/png, image/jpg, application/pdf
    content_type = file.content_type
    if content_type not in ("image/png", "image/jpeg", "application/pdf"):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    job_id = str(uuid.uuid4())
    save_path = save_upload_file(file, settings.UPLOAD_DIR, job_id)
    append_audit({"event": "upload_received", "job_id": job_id, "filename": save_path})
    if sync:
        # run synchronously by calling task function directly
        from tasks import ocr_task as taskfunc
        res = taskfunc.run(job_id, save_path)
        return JSONResponse(content=res)
    else:
        # dispatch celery job
        ocr_task.apply_async(args=(job_id, save_path), queue="ocr_queue")
        return {"job_id": job_id, "status": "queued"}

@router.get("/status/{job_id}")
async def status(job_id: str):
    res = load_result_json(job_id, settings.OUTPUT_DIR)
    if res:
        return {"job_id": job_id, "status": "done", "result": res}
    else:
        # check for queued/running is best-effort via outputs folder
        return {"job_id": job_id, "status": "processing_or_not_found"}

@router.get("/boxes")
async def boxes(path: str):
    # run pytesseract.image_to_data and return boxes
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Path not found")
    tess = TesseractPipeline()
    boxes = tess.image_to_boxes(path)
    return boxes

@router.post("/verify")
async def verify(payload: dict):
    """
    payload:
    {
      "job_id": "...",
      "form_data": {...}
    }
    """
    from utils.fuzzy import verify_fields
    job_id = payload.get("job_id")
    form_data = payload.get("form_data", {})
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id required")
    res = load_result_json(job_id, settings.OUTPUT_DIR)
    if not res:
        raise HTTPException(status_code=404, detail="job not found")
    extracted = res.get("fields", {})
    verification, overall = verify_fields(extracted, form_data)
    # generate report
    from utils.pdf_report import generate_verification_report
    report_path = os.path.join(settings.OUTPUT_DIR, f"{job_id}_verification.pdf")
    generate_verification_report(job_id, extracted, form_data, verification, overall, report_path)
    append_audit({"event": "verification_done", "job_id": job_id, "score": overall, "report": report_path})
    return {"verification": verification, "overall_score": overall, "report": report_path}
