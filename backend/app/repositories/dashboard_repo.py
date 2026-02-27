from typing import List, Any
from datetime import datetime
from sqlalchemy.orm import Session,joinedload
from sqlalchemy import func, case, desc
from typing import Optional

# Đảm bảo đường dẫn import models đúng với dự án của bạn
from app.models.models import Users, Messages, ForumPosts, Reports, Conversations

class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def count_total_users(self) -> int:
        return self.db.query(Users).count()

    def count_new_users(self, start_of_day: datetime) -> int:
        return self.db.query(Users).filter(Users.created_at >= start_of_day).count()

    def count_total_messages(self) -> int:
        return self.db.query(Messages).count()
    
    def count_new_conversations(self, start_of_day: datetime) -> int:
        """Đếm số cuộc hội thoại mới được tạo từ đầu ngày"""
        return self.db.query(Conversations).filter(Conversations.created_at >= start_of_day).count()

    def count_active_posts(self) -> int:
        return self.db.query(ForumPosts).filter(ForumPosts.status == 'active').count()

    def count_pending_reports(self) -> int:
        return self.db.query(Reports).filter(Reports.status == 'pending').count()

    def count_active_users_24h(self, time_threshold: datetime) -> int:
        return self.db.query(Users.id)\
            .join(Conversations, Users.conversations)\
            .join(Messages, Conversations.messages)\
            .filter(Messages.created_at >= time_threshold)\
            .distinct().count()

    def get_message_stats_by_date(self, start_date: datetime) -> List[Any]:
        return self.db.query(
            func.date(Messages.created_at).label('date'),
            func.sum(case((Messages.role == 'user', 1), else_=0)).label('user_count'),
            func.sum(case((Messages.role != 'user', 1), else_=0)).label('ai_count')
        ).filter(
            Messages.created_at >= start_date
        ).group_by(
            func.date(Messages.created_at)
        ).order_by(
            func.date(Messages.created_at)
        ).all()

    def get_recent_pending_reports(self, limit: int = 5) -> List[Reports]:
        return self.db.query(Reports)\
            .options(joinedload(Reports.reporter))\
            .filter(Reports.status == 'pending')\
            .order_by(desc(Reports.created_at))\
            .limit(limit)\
            .all()
    
    def get_report_by_id(self, report_id: int) -> Optional[Reports]:
        """Lấy một báo cáo cụ thể dựa vào ID"""
        return self.db.query(Reports).filter(Reports.id == report_id).first()