from Levenshtein import distance as lev_distance
from config import settings
from typing import Dict, Any

def similarity(a: str, b: str) -> float:
    a = (a or "").strip()
    b = (b or "").strip()
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    d = lev_distance(a, b)
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 1.0
    return 1.0 - (d / max_len)

def classify(sim: float) -> str:
    if sim >= settings.MIN_MATCH_SIMILARITY:
        return "match"
    if sim >= settings.MIN_PARTIAL_SIMILARITY:
        return "partial"
    return "mismatch"

def verify_fields(extracted: Dict[str, Any], submitted: Dict[str, Any]):
    verification = {}
    total = 0.0
    count = 0
    for k, ex in extracted.items():
        ex_val = ex.get("value", "")
        sub_val = submitted.get(k, "")
        sim = similarity(ex_val, sub_val)
        status = classify(sim)
        verification[k] = {
            "submitted": sub_val,
            "extracted": ex_val,
            "similarity": round(sim, 3),
            "status": status,
            "confidence": round(sim,3)
        }
        total += sim
        count += 1
    overall = round((total / max(count,1)), 3)
    return verification, overall
