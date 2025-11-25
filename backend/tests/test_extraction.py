import os
import json
from pathlib import Path
from config import settings
from ocr.extract_fields import extract_fields

def test_sample_extraction():
    # locate sample image
    runtime_path = settings.SAMPLE_IMAGE_RUNTIME
    local_path = settings.SAMPLE_IMAGE_LOCAL
    path = runtime_path if os.path.exists(runtime_path) else local_path
    assert os.path.exists(path), f"Sample image not found at {path}. Please copy sample image there."
    # Instead of running full heavy model in test env, we run Tesseract quick pipeline to confirm structure
    from ocr.tesseract_pipeline import TesseractPipeline
    t = TesseractPipeline()
    res = t.predict(path_to_pil := path)  # pipeline accepts path in image_to_boxes usage; we call predict by reading pil image in the pipeline
    # we can't assert content; just ensure fields extraction returns keys
    fields = extract_fields(res.get("text",""))
    expected_keys = {"name","age","gender","email","phone","address","date_of_birth"}
    assert expected_keys.issubset(set(fields.keys()))
    # confidence sanity checks
    for k,v in fields.items():
        assert 0.0 <= float(v.get("confidence",0.0)) <= 1.0
