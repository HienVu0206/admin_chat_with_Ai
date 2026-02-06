from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.repositories.dashboard_repo import DashboardRepository
from app.schemas.dashboard_schema import (
    DashboardSummaryResponse, 
    MessageChartPoint, 
    PendingReportItem
)

class DashboardService:
    def __init__(self, db: Session):
        self.repo = DashboardRepository(db)

    def get_summary_stats(self) -> DashboardSummaryResponse:
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        last_24h = now - timedelta(hours=24)

        return DashboardSummaryResponse(
            total_users=self.repo.count_total_users(),
            new_users_today=self.repo.count_new_users(start_of_day),
            active_users_24h=self.repo.count_active_users_24h(last_24h),
            total_messages=self.repo.count_total_messages(),
            new_conversations_today=self.repo.count_new_conversations(start_of_day),
            total_posts=self.repo.count_active_posts(),
            pending_reports=self.repo.count_pending_reports()
        )

    def get_message_chart_data(self, days: int) -> List[MessageChartPoint]:
        start_date = datetime.now() - timedelta(days=days)
        results = self.repo.get_message_stats_by_date(start_date)
        
        chart_data = []
        for row in results:
            chart_data.append(MessageChartPoint(
                date=str(row.date),
                user_count=int(row.user_count or 0),
                ai_count=int(row.ai_count or 0)
            ))
        return chart_data

    def get_pending_reports(self, limit: int = 5) -> List[PendingReportItem]:
        raw_reports = self.repo.get_recent_pending_reports(limit)
        
        cleaned_reports = []
        for r in raw_reports:
            target = "Unknown"
            if r.post_id: target = "Post"
            elif r.comment_id: target = "Comment"
            elif r.reported_user_id: target = "User"

            reporter_name = r.reporter.full_name if r.reporter else "Unknown User"

            cleaned_reports.append(PendingReportItem(
                id=r.id,
                reason=r.reason,
                created_at=r.created_at,
                reporter_name=reporter_name,
                status=r.status,
                target_type=target
            ))
            
        return cleaned_reports