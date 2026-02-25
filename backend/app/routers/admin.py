from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.admin_service import AdminService
from app.schemas.admin_schema import LoginRequest, TokenResponse

router = APIRouter(prefix="/admin", tags=["Admin Auth"])

# Hàm khởi tạo Service chuẩn DI (Dependency Injection)
def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(db)

@router.post("/login", response_model=TokenResponse)
async def admin_login(
    data: LoginRequest, 
    service: AdminService = Depends(get_admin_service)
):
    # Lúc này service đã được tiêm sẵn db, chỉ cần truyền email và password
    return service.login_admin(data.email, data.password)