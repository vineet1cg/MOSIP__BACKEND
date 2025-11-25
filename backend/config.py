import os
from pydantic import BaseSettings, AnyUrl

class Settings(BaseSettings):
    APP_NAME: str = "ocr-backend"
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/app/uploads")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "/app/outputs")
    SAMPLE_IMAGE_RUNTIME: str = os.getenv("SAMPLE_IMAGE_RUNTIME", "/mnt/data/99dcb476-3358-469f-930e-75e0a155a2d6.png")
    SAMPLE_IMAGE_LOCAL: str = os.getenv("SAMPLE_IMAGE_LOCAL", "/app/samples/sample1.png")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = ""  # manual JSON storage
    TROCR_MODEL: str = os.getenv("TROCR_MODEL", "microsoft/trocr-base-handwritten")
    TROCR_DEVICE: str = os.getenv("TROCR_DEVICE", "cpu")
    # Ensemble thresholds
    TROCR_CONF_THRESHOLD: float = float(os.getenv("TROCR_CONF_THRESHOLD", "0.75"))
    MIN_PARTIAL_SIMILARITY: float = float(os.getenv("MIN_PARTIAL_SIMILARITY", "0.60"))
    MIN_MATCH_SIMILARITY: float = float(os.getenv("MIN_MATCH_SIMILARITY", "0.90"))

settings = Settings()
