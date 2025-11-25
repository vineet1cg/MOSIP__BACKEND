import os
from pathlib import Path
import shutil
import json

def save_upload_file(upload_file, upload_dir, job_id):
    os.makedirs(upload_dir, exist_ok=True)
    extension = upload_file.filename.split(".")[-1]
    destination_file_path = os.path.join(upload_dir, f"{job_id}.{extension}")
    with open(destination_file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return destination_file_path

def save_json_result(job_id, payload, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{job_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path

def load_result_json(job_id, output_dir):
    path = os.path.join(output_dir, f"{job_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
