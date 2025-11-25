from fastapi import FastAPI
from routers import ocr, audit, health

def create_app():
    app = FastAPI(title="OCR Backend")
    app.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
    app.include_router(audit.router, prefix="/audit", tags=["audit"])
    app.include_router(health.router, prefix="/health", tags=["health"])
    return app

app = create_app()
