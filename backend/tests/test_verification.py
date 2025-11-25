import os
from utils.fuzzy import verify_fields
import json

def test_verification_matches_ground_truth():
    # load ground truth
    base = os.path.dirname(__file__)
    gt_path = os.path.join(base, "ground_truth", "sample1.json")
    assert os.path.exists(gt_path)
    with open(gt_path, "r", encoding="utf-8") as f:
        gt = json.load(f)
    extracted = gt.get("extracted", {})
    submitted = gt.get("submitted", {})
    verification, overall = verify_fields(extracted, submitted)
    # ensure verification entries for keys
    for k in extracted.keys():
        assert k in verification
        sim = verification[k]["similarity"]
        assert 0.0 <= sim <= 1.0
    # overall is average: between 0 and 1
    assert 0.0 <= overall <= 1.0
