import redis
import redis.asyncio as redis_async
from typing import AsyncGenerator
from app.core.config import settings

# =====================================================================
# =====================================================================
# Sử dụng decode_responses=True để Redis trả về string thay vì bytes
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


# =====================================================================
# =====================================================================
async def get_redis() -> AsyncGenerator[redis_async.Redis, None]:
    """
    Dependency cung cấp Redis client (async) cho mỗi request.
    Dùng chung với FastAPI Depends()
    """
    client = redis_async.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        # Đảm bảo đóng kết nối an toàn sau khi API trả về kết quả
        await client.aclose()