from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import redis.asyncio as redis

from app.core.database import get_db
# Giả sử file cấu hình redis của sếp nằm ở core/redis_client.py
from app.core.redis_client import get_redis 

from app.schemas.chat_schema import ConversationResponse
from app.services.chat_service import get_conversations_service
# Sếp có thể import get_current_admin để bảo mật API này nếu cần
from app.core.security import get_current_admin
from app.models.models import Users

router = APIRouter(prefix="/admin/conversations", tags=["Admin Conversations"])

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    search: Optional[str] = Query(None, description="Tìm theo tên user hoặc title đoạn chat"),
    db: Session = Depends(get_db),
    r: redis.Redis = Depends(get_redis),
    admin: Users = Depends(get_current_admin) # Bắt buộc phải là Admin mới xem được
):
    """
    API lấy danh sách toàn bộ đoạn chat của hệ thống (Áp dụng Redis Cache).
    """
    # Vì tầng Service có gọi await (do dùng redis.asyncio) nên Router phải là async def
    result = await get_conversations_service(db=db, redis_client=r, search=search)
    return result