import re
from typing import Dict, Any
from collections import defaultdict
import spacy
from config import settings

# Try to load spaCy model, fallback gracefully
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

EMAIL_RE = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
PHONE_RE = re.compile(r"(\+?\d{7,3}[\d\-\s]{3,}\d{2,})")
DATE_RE = re.compile(r"(\d{1,2}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{2,4})")
AGE_RE = re.compile(r"\b(?:age|aged)[:\s]*([0-9]{1,3})\b", re.IGNORECASE)
GENDER_RE = re.compile(r"\b(male|female|other|m|f)\b", re.IGNORECASE)

def candidate_box(values):
    # format list
    return [{"value": v, "confidence": 0.5} for v in values]

def extract_fields(text: str) -> Dict[str, Any]:
    out = {}
    txt = text or ""
    # email
    emails = EMAIL_RE.findall(txt)
    out['email'] = {
        "value": emails[0] if emails else "",
        "confidence": 0.9 if emails else 0.0,
        "candidates": candidate_box(emails)
    }
    # phone
    phones = PHONE_RE.findall(txt)
    phones_clean = [re.sub(r"[^\d\+]", "", p) for p in phones]
    out['phone'] = {
        "value": phones_clean[0] if phones_clean else "",
        "confidence": 0.85 if phones_clean else 0.0,
        "candidates": candidate_box(phones_clean)
    }
    # date_of_birth
    dates = DATE_RE.findall(txt)
    out['date_of_birth'] = {
        "value": dates[0] if dates else "",
        "confidence": 0.8 if dates else 0.0,
        "candidates": candidate_box(dates)
    }
    # age
    ages = AGE_RE.findall(txt)
    out['age'] = {
        "value": ages[0] if ages else "",
        "confidence": 0.7 if ages else 0.0,
        "candidates": candidate_box(ages)
    }
    # gender
    genders = GENDER_RE.findall(txt)
    out['gender'] = {
        "value": genders[0] if genders else "",
        "confidence": 0.6 if genders else 0.0,
        "candidates": candidate_box(genders)
    }
    # name using heuristics + spaCy NER
    name = ""
    candidates = []
    if nlp:
        doc = nlp(txt)
        ents = [ent.text for ent in doc.ents if ent.label_ in ("PERSON",)]
        if ents:
            name = ents[0]
            candidates = ents
    if not name:
        # heuristic: first two capitalized words
        m = re.search(r"\b([A-Z][a-z]{1,}\s+[A-Z][a-z]{1,})\b", txt)
        if m:
            name = m.group(1)
            candidates = [name]
    out['name'] = {
        "value": name,
        "confidence": 0.75 if name else 0.0,
        "candidates": candidate_box(candidates) if candidates else []
    }
    # address: heuristic: lines containing numbers + street keywords
    addresses = re.findall(r"((?:\d{1,4}\s+\w+(?:\s+\w+){0,6}\,?.{0,60}))", txt)
    out['address'] = {
        "value": addresses[0] if addresses else "",
        "confidence": 0.6 if addresses else 0.0,
        "candidates": candidate_box(addresses)
    }
    return out
