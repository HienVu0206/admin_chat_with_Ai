from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

# Thêm import hàm này ở đầu file nếu chưa có
from app.services.dashboard_service import calculate_daily_stats 
from app.core.database import get_db
from app.services.dashboard_service import DashboardService

# --- SỬA Ở ĐÂY: Bổ sung DailyStatItem ---
from app.schemas.dashboard_schema import (
    DashboardSummaryResponse, 
    MessageChartPoint, 
    PendingReportItem,
    DailyStatItem
)
# Nhớ import thêm Messages và DashboardDailyStats để dùng cho hàm nạp bù
from app.models.models import Users, Messages, DashboardDailyStats
from app.core.security import get_current_admin

# Khai báo dependencies ở mức Router để bảo vệ TẤT CẢ các API bên trong
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_admin)] # BẮT BUỘC PHẢI LÀ ADMIN
)

def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    service: DashboardService = Depends(get_dashboard_service)
):
    return service.get_summary_stats()

# (Có thể bạn sẽ không cần API này nữa nếu dùng API cron_stats bên dưới để vẽ biểu đồ)
@router.get("/charts/messages", response_model=List[MessageChartPoint])
def get_message_chart(
    days: int = Query(7),
    service: DashboardService = Depends(get_dashboard_service)
):
    return service.get_message_chart_data(days)

@router.get("/reports/pending", response_model=List[PendingReportItem])
def get_recent_reports(
    limit: int = Query(5),
    service: DashboardService = Depends(get_dashboard_service)
):
    return service.get_pending_reports(limit)

# ==========================================
# --- API LẤY DỮ LIỆU TỪ CRONJOB (Đã chuẩn hóa) ---
# ==========================================
@router.get("/cron_stats", response_model=List[DailyStatItem])
def get_daily_cronjob_stats(
    days: int = Query(7, description="Số ngày muốn lấy dữ liệu"),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    API lấy dữ liệu thống kê từ bảng DashboardDailyStats (do Cronjob chạy mỗi đêm)
    Dùng để gọi ra vẽ biểu đồ trên Frontend.
    """
    # Gọi logic từ Service, Schema sẽ tự động convert dữ liệu thành JSON chuẩn
    return service.get_cronjob_stats(days)


@router.post("/run-cronjob-now")
def run_cronjob_manually(db: Session = Depends(get_db)):
    calculate_daily_stats(db)
    return {"message": "Đã chạy hàm tổng hợp dữ liệu thành công!"}


# ==========================================
# --- API NẠP BÙ DỮ LIỆU (CHẠY 1 LẦN) ---
# ==========================================
@router.post("/backfill-7-days")
def backfill_7_days_manually(db: Session = Depends(get_db)):
    """
    API dùng 1 lần để quay ngược thời gian, nạp bù dữ liệu 7 ngày qua 
    vào bảng DashboardDailyStats để test biểu đồ.
    """
    today = datetime.now().date()
    
    # Chạy vòng lặp lùi về 7 ngày trước (từ hôm nay lùi về 6 ngày trước = 7 ngày)
    for i in range(7):
        target_date = today - timedelta(days=i)
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        # 1. Lọc đếm tin nhắn trong đúng ngày target_date đó
        messages_day = db.query(Messages.role, func.count(Messages.id))\
            .filter(Messages.created_at >= start_of_day, Messages.created_at <= end_of_day)\
            .group_by(Messages.role).all()
            
        u_count = 0
        ai_count = 0
        for role, count in messages_day:
            if role == 'user': 
                u_count = count
            elif role == 'assistant': 
                ai_count = count
                
        # 2. Kiểm tra xem ngày đó đã có trong bảng chưa
        stat_record = db.query(DashboardDailyStats).filter(DashboardDailyStats.date == target_date).first()
        
        if not stat_record:
            # Nếu chưa có thì tạo mới
            stat_record = DashboardDailyStats(
                date=target_date,
                total_users=0, # Bỏ qua đếm user cũ cho nhanh, chủ yếu lấy tin nhắn test biểu đồ
                active_users=0,
                new_chats=0,
                total_messages=u_count + ai_count,
                user_msg_count=u_count,
                ai_bot_msg_count=ai_count
            )
            db.add(stat_record)
        else:
            # Nếu có rồi thì cập nhật lại số liệu
            stat_record.user_msg_count = u_count
            stat_record.ai_bot_msg_count = ai_count
            stat_record.total_messages = u_count + ai_count
            
        db.commit()

    return {"message": "✅ Đã nạp bù thành công dữ liệu 7 ngày qua vào bảng thống kê!"}