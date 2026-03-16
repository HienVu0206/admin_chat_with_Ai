import json
import redis.asyncio as redis
from sqlalchemy.orm import Session
from typing import Optional

from app.repositories.chat_repo import get_all_conversations_db

async def get_conversations_service(
    db: Session, 
    redis_client: redis.Redis, 
    search: Optional[str] = None
):
    # 1. Tạo Cache Key linh hoạt dựa trên search
    if search:
        safe_term = search.strip().lower()
        cache_key = f"admin:conversations:search:{safe_term}"
    else:
        cache_key = "admin:conversations:all"

    # 2. Kiểm tra Redis Cache
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        print(f"🚀 Lấy data từ Redis Cache (Key: {cache_key})")
        return json.loads(cached_data)

    # 3. Cache Miss -> Gọi xuống Repository
    print("🐢 Truy vấn Database...")
    db_results = get_all_conversations_db(db, search)

    # 4. Format data để lưu được vào Redis (Serialize ra JSON)
    result_list = []
    for row in db_results:
        result_list.append({
            "id": row.id,
            "user_name": row.user_name,
            "title": row.title,
            # Chuyển Datetime thành chuỗi ISO format để dùng json.dumps
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None
        })

    # 5. Lưu kết quả vào Redis Cache với TTL = 300 giây (5 phút)
    await redis_client.set(cache_key, json.dumps(result_list), ex=300)

    return result_list