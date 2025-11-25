import uuid
import time
import json
from pathlib import Path
from celery_app import celery
from config import settings
from ocr.preprocess import preprocess_image_from_path
from ocr.trocr_pipeline import TroCRPipeline
from ocr.tesseract_pipeline import TesseractPipeline
from ocr.ensemble import ensemble_fuse
from ocr.extract_fields import extract_fields
from utils.audit import append_audit
from utils.storage import save_json_result

trocr = TroCRPipeline(model_name=settings.TROCR_MODEL, device=settings.TROCR_DEVICE)
tess = TesseractPipeline()

@celery.task(name="ocr_task", bind=True)
def ocr_task(self, job_id: str, path: str):
    started = time.time()
    job_id = job_id or str(uuid.uuid4())
    append_audit({"event": "task_started", "job_id": job_id, "path": path})
    # Preprocess
    pre = preprocess_image_from_path(path)
    # Run TroCR
    trocr_res = trocr.predict(pre["pil_rgb"])
    # Run Tesseract
    tess_res = tess.predict(pre["pil_rgb"])
    # Ensemble
    ensemble_res = ensemble_fuse(trocr_res, tess_res, settings)
    # Fields
    fields = extract_fields(ensemble_res["text"])
    meta = {
        "trocr_conf": trocr_res.get("score"),
        "tesser_conf": tess_res.get("score"),
        "chosen_source": ensemble_res.get("chosen"),
        "processing_time": round(time.time() - started, 3),
        "quality": pre.get("quality", {}),
    }
    result = {
        "job_id": job_id,
        "text": ensemble_res["text"],
        "fields": fields,
        "meta": meta,
    }
    # save
    save_json_result(job_id, result, settings.OUTPUT_DIR)
    append_audit({"event": "task_finished", "job_id": job_id, "result_path": f"{settings.OUTPUT_DIR}/{job_id}.json"})
    return result
