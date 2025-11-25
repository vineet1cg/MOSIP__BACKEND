import os
from fastapi import APIRouter
from config import settings
from utils.audit import append_audit

router = APIRouter()

@router.post("")
async def audit(payload: dict):
    append_audit(payload)
    return {"status": "ok"}
