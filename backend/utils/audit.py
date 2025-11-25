import json
import os
from datetime import datetime
from config import settings

AUDIT_FILE = os.path.join(settings.OUTPUT_DIR, "audit.log")

def append_audit(payload: dict):
    payload = payload.copy()
    payload.setdefault("timestamp", datetime.utcnow().isoformat()+"Z")
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload)+"\n")
