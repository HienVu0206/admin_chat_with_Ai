from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List
import redis
from fastapi import HTTPException, status
import logging
from app.models.models import Users, Conversations, Messages, DashboardDailyStats
from sqlalchemy import func
from datetime import date, datetime
from app.repositories.dashboard_repo import DashboardRepository
from app.schemas.dashboard_schema import (
    DashboardSummaryResponse, 
    MessageChartPoint, 
    PendingReportItem
)
# Nhớ tạo file redis_client.py và cấu hình như hướng dẫn trước đó
from app.core.redis_client import redis_client
from app.core.config import settings

# --- BỔ SUNG 1: Import Model DashboardDailyStats ---
from app.models.models import DashboardDailyStats

logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(self, db: Session):
        self.db = db  # QUAN TRỌNG: Đã thêm dòng này để fix lỗi AttributeError
        self.repo = DashboardRepository(db)
        self.redis = redis_client
        
    def get_summary_stats(self) -> DashboardSummaryResponse:
        cache_key = "dashboard:summary_stats"
        cached_data = None

        # 1. Thử lấy từ Cache an toàn
        try:
            cached_data = self.redis.get(cache_key)
        except redis.exceptions.ConnectionError as e:
            logger.warning(f"⚠️ Không thể kết nối Redis (GET): {e}")
            # Mặc kệ lỗi, để cached_data = None và chạy tiếp xuống DB

        if cached_data:
            return DashboardSummaryResponse.model_validate_json(cached_data)

        # 2. Nếu không có Cache (hoặc Redis sập), query từ Database
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        last_24h = now - timedelta(hours=24)

        response = DashboardSummaryResponse(
            total_users=self.repo.count_total_users(),
            new_users_today=self.repo.count_new_users(start_of_day),
            active_users_24h=self.repo.count_active_users_24h(last_24h),
            total_messages=self.repo.count_total_messages(),
            new_conversations_today=self.repo.count_new_conversations(start_of_day),
            total_posts=self.repo.count_active_posts(),
            pending_reports=self.repo.count_pending_reports()
        )

        # 3. Thử lưu vào Cache an toàn
        try:
            cache_ttl = getattr(settings, 'CACHE_EXPIRE_SECONDS', 300) 
            self.redis.setex(
                name=cache_key,
                time=cache_ttl,
                value=response.model_dump_json()
            )
        except redis.exceptions.ConnectionError as e:
            logger.warning(f"⚠️ Không thể kết nối Redis (SET): {e}")
            # Mặc kệ lỗi, vì đằng nào data DB cũng đã được lấy và sẵn sàng trả về

        return response

    def get_message_chart_data(self, days: int) -> List[MessageChartPoint]:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
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
    
    def handle_report(self, report_id: int, action: str) -> dict:
        """
        Xử lý báo cáo: action có thể là 'resolved' (duyệt) hoặc 'rejected' (từ chối)
        """
        # 1. Tìm báo cáo trong Database
        report = self.repo.get_report_by_id(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Không tìm thấy báo cáo này"
            )

        if report.status != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Báo cáo này đã được xử lý (trạng thái hiện tại: {report.status})"
            )

        # 2. Cập nhật trạng thái và lưu vào DB
        report.status = action
        self.db.commit() # Code hiện tại đã chạy mượt mà vì self.db đã được khởi tạo

        # 3. XÓA CACHE DASHBOARD NGAY LẬP TỨC
        # Để khi Admin quay lại trang chủ, số lượng "Báo cáo chờ xử lý" sẽ giảm xuống ngay
        self.invalidate_summary_cache()

        return {
            "status": "success",
            "message": f"Báo cáo #{report_id} đã được chuyển sang trạng thái: {action}"
        }

    def invalidate_summary_cache(self):
        """
        Gọi hàm này bất cứ khi nào dữ liệu tổng quan thay đổi
        (VD: Có user mới đăng ký, Admin duyệt report, Admin khóa tài khoản...)
        """
        cache_key = "dashboard:summary_stats"
        try:
            self.redis.delete(cache_key)
        except redis.exceptions.ConnectionError:
            pass # Nếu Redis sập thì thôi, không cần xóa cache

    # ==========================================
    # --- BỔ SUNG 2: Hàm truy vấn dữ liệu Cronjob ---
    # ==========================================
    def get_cronjob_stats(self, days: int):
        """
        Truy vấn dữ liệu từ bảng DashboardDailyStats do Cronjob tổng hợp mỗi đêm
        """
        stats = self.db.query(DashboardDailyStats)\
                       .order_by(DashboardDailyStats.date.desc())\
                       .limit(days)\
                       .all()
        # Đảo ngược để dữ liệu xếp theo thứ tự thời gian từ cũ tới mới (dành cho việc vẽ biểu đồ)
        stats.reverse()
        return stats
    
    # Nhớ thêm 2 dòng import này ở đầu file dashboard_service.py nếu chưa có nhé:
# from sqlalchemy import func
# from app.models.models import Users, Conversations, Messages

# Dán hàm này xuống DƯỚI CÙNG của file dashboard_service.py (bên ngoài class DashboardService)
# def calculate_daily_stats(db: Session):
#     """
#     Hàm này dùng để Cronjob chạy mỗi đêm, quét toàn bộ DB và lưu chốt sổ vào bảng DashboardDailyStats
#     """
#     today = date.today()
#     start_of_day = datetime.combine(today, datetime.min.time())
    
#     print(f"Bắt đầu tổng hợp dữ liệu cho ngày: {today}")

#     # 1. Tổng người dùng
#     total_users = db.query(func.count(Users.id)).scalar() or 0

#     # 2. User hoạt động trong 24h qua
#     active_users = db.query(func.count(func.distinct(Conversations.user_id)))\
#         .join(Messages, Messages.conversation_id == Conversations.id)\
#         .filter(Messages.created_at >= start_of_day).scalar() or 0

#     # 3. Số đoạn chat mới tạo trong hôm nay
#     new_chats = db.query(func.count(Conversations.id))\
#         .filter(Conversations.created_at >= start_of_day).scalar() or 0

#     # 4. Tổng tin nhắn toàn hệ thống
#     total_messages = db.query(func.count(Messages.id)).scalar() or 0

#     # 5. Tỷ lệ tin nhắn User / AI trong hôm nay
#     messages_today = db.query(Messages.role, func.count(Messages.id))\
#         .filter(Messages.created_at >= start_of_day)\
#         .group_by(Messages.role).all()
    
#     user_msg_count = 0
#     ai_bot_msg_count = 0
    
#     for role, count in messages_today:
#         if role == 'user':
#             user_msg_count = count
#         elif role == 'assistant':
#             ai_bot_msg_count = count

#     # --- LƯU VÀO DATABASE ---
#     stat_record = db.query(DashboardDailyStats).filter(DashboardDailyStats.date == today).first()
    
#     if not stat_record:
#         stat_record = DashboardDailyStats(
#             date=today,
#             total_users=total_users,
#             active_users=active_users,
#             new_chats=new_chats,
#             total_messages=total_messages,
#             user_msg_count=user_msg_count,
#             ai_bot_msg_count=ai_bot_msg_count
#         )
#         db.add(stat_record)
#     else:
#         stat_record.total_users = total_users
#         stat_record.active_users = active_users
#         stat_record.new_chats = new_chats
#         stat_record.total_messages = total_messages
#         stat_record.user_msg_count = user_msg_count
#         stat_record.ai_bot_msg_count = ai_bot_msg_count

#     db.commit()
#     print(f"✅ Đã lưu thành công dữ liệu ngày {today} vào bảng DashboardDailyStats!")