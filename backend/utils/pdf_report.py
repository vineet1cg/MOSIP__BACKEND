from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import json
import os

def generate_verification_report(job_id, extracted_fields, corrected_fields, verification, overall_score, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 50, f"OCR Verification Report - Job {job_id}")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, f"Timestamp: {datetime.utcnow().isoformat()}Z")
    y = height - 100
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Extracted Fields:")
    y -= 20
    c.setFont("Helvetica", 10)
    for k, v in extracted_fields.items():
        c.drawString(50, y, f"{k}: {v.get('value','')} (confidence: {v.get('confidence',0)})")
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 40
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Corrected / Submitted Fields:")
    y -= 20
    c.setFont("Helvetica", 10)
    for k, v in corrected_fields.items():
        c.drawString(50, y, f"{k}: {v}")
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 40
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Verification Details:")
    y -= 20
    c.setFont("Helvetica", 10)
    for k, v in verification.items():
        c.drawString(50, y, f"{k}: status={v['status']}, similarity={v['similarity']}")
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 40
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, f"Overall Verification Score: {overall_score}")
    c.save()
    return output_path
