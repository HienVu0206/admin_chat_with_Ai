from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard_schema import DashboardSummaryResponse, MessageChartPoint, PendingReportItem
from app.models.models import Users
from app.core.security import get_current_admin # THÊM IMPORT NÀY

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