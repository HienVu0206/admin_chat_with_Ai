from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- 1. Schema cho các Card thống kê (Summary) ---
class DashboardSummaryResponse(BaseModel):
    total_users: int
    new_users_today: int
    active_users_24h: int
    total_messages: int
    new_conversations_today: int  # Trường đếm số đoạn chat mới
    total_posts: int
    pending_reports: int

# --- 2. Schema cho Biểu đồ (Messages Chart) ---
class MessageChartPoint(BaseModel):
    date: str          
    user_count: int
    ai_count: int

# --- 3. Schema cho Báo cáo chưa xử lý (Pending Reports) ---
class PendingReportItem(BaseModel):
    id: int
    reason: Optional[str] = None
    created_at: datetime
    reporter_name: str
    status: str
    target_type: str  # 'Post', 'Comment', 'User'

    class Config:
        from_attributes = True