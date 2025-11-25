from celery import Celery
from config import settings

celery = Celery(
    "ocr_tasks",
    broker=settings.CELERY_BROKER_URL,
)

# don't use result backend; we'll store results manually
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    enable_utc=True,
)
