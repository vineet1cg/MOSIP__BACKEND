from fastapi import APIRouter
from config import settings
import redis
from utils.logger import get_logger

router = APIRouter()
logger = get_logger()

@router.get("")
async def health():
    ok = True
    redis_ok = False
    try:
        r = redis.StrictRedis.from_url(settings.REDIS_URL, socket_timeout=2)
        redis_ok = r.ping()
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
    return {"status": "ok" if redis_ok else "degraded", "redis": redis_ok}
