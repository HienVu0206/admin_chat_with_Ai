# --- app/core/redis_client.py ---
import redis
from app.core.config import settings

# Sử dụng decode_responses=True để Redis trả về string thay vì bytes
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)