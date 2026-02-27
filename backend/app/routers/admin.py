from typing import List
from fastapi import APIRouter, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import verify_refresh_token
from app.core.database import get_db
from app.services.admin_service import AdminService
from app.services.role_service import RoleService      # <-- THÊM IMPORT SERVICE CHO ROLE
from app.schemas.admin_schema import TokenResponse
from app.schemas.role import RoleResponse              # <-- THÊM IMPORT SCHEMA CHO ROLE

# Giữ nguyên prefix /admin
router = APIRouter(prefix="/admin")

# ==========================================
# DEPENDENCY INJECTION (Khởi tạo Service)
# ==========================================
def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(db)

def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    return RoleService(db)


# ==========================================
# ROUTES: ADMIN AUTH (Đăng nhập & Token)
# ==========================================
@router.post("/login", response_model=TokenResponse, tags=["Admin Auth"])
async def admin_login(
    # Sử dụng form_data theo chuẩn OAuth2 thay vì JSON body
    form_data: OAuth2PasswordRequestForm = Depends(), 
    service: AdminService = Depends(get_admin_service)
):
    # Swagger mặc định gửi 2 trường là 'username' và 'password' dưới dạng Form-Data.
    # Chúng ta quy ước lấy giá trị 'username' đó để truyền vào tham số 'email' của hàm login.
    return service.login_admin(email=form_data.username, password=form_data.password)


@router.post("/refresh-token", response_model=TokenResponse, tags=["Admin Auth"])
async def refresh_access_token(
    refresh_token: str = Body(..., embed=True), # Client gửi JSON: {"refresh_token": "..."}
    db: Session = Depends(get_db),
    service: AdminService = Depends(get_admin_service)
):
    """Sử dụng Refresh Token để lấy Access Token mới khi bị hết hạn"""
    # 1. Xác thực refresh token
    user = verify_refresh_token(refresh_token, db)
    
    # 2. Tạo token mới
    new_access_token = service.auth_service.create_access_token(
        data={"sub": str(user.id), "role": user.role.name}
    )
    new_refresh_token = service.auth_service.create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        role=user.role.name
    )


# ==========================================
# ROUTES: ADMIN MANAGEMENT (Quản lý dữ liệu)
# ==========================================
@router.get("/roles", response_model=List[RoleResponse], tags=["Admin Management"])
async def get_all_roles(
    service: RoleService = Depends(get_role_service)
    # Tương lai bạn nên thêm: current_admin = Depends(get_current_admin_user) để bảo mật
):
    """Lấy danh sách tất cả các quyền hạn (Roles) từ database"""
    return service.get_all_roles()