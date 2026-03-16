from fastapi import APIRouter, Depends
from typing import List
import redis.asyncio as redis

# Import từ các module khác trong project của sếp
from app.schemas.chat_schema import ChatSession
from app.services.chat_service import get_user_chat_list_service

# Lấy hàm get_redis mà sếp đã viết lúc đầu (Giả sử sếp để nó trong file app/core/redis_client.py)
# Nếu sếp để file khác thì nhớ sửa lại đường dẫn import này nhé
from app.core.redis_client import get_redis 

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.get("/users/{user_id}", response_model=List[ChatSession])
async def get_chats(user_id: str, r: redis.Redis = Depends(get_redis)):
    """
    API lấy danh sách đoạn chat của User (Có áp dụng Redis Cache)
    """
    # Ném data sang Service xử lý cho gọn Router
    result = await get_user_chat_list_service(user_id=user_id, redis_client=r)
    return result