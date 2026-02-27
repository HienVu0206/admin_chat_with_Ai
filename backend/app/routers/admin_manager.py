from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional # Sửa lỗi NameError đã gặp ở Terminal

from app.core.database import get_db
from app.models.models import Users
# Sử dụng đúng đường dẫn bảo mật bạn đã yêu cầu
from app.core.security import get_current_admin 
from app.schemas.admin_schema import (
    ChangeRoleRequest, 
    AuditLogResponse, 
    UserAdminResponse, 
    RoleResponse, 
    RoleCreateRequest
)
from app.services.admin_service import AdminManagementService

router = APIRouter(prefix="/admin", tags=["Admin Management"])

# Dependency để khởi tạo nhanh Service
def get_management_service(db: Session = Depends(get_db)):
    return AdminManagementService(db)

# --- 1. QUẢN LÝ NGƯỜI DÙNG ---

@router.get("/users", response_model=List[UserAdminResponse])
def get_users_list(
    role_id: Optional[int] = Query(None, description="Lọc theo ID chức vụ"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên hoặc email"),
    service: AdminManagementService = Depends(get_management_service),
    current_admin: Users = Depends(get_current_admin)
):
    """Lấy danh sách người dùng kèm bộ lọc và tìm kiếm"""
    return service.list_users(role_id, search)

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    data: ChangeRoleRequest,
    service: AdminManagementService = Depends(get_management_service),
    current_admin: Users = Depends(get_current_admin)
):
    """Cập nhật chức vụ cho người dùng cụ thể và ghi log"""
    return service.change_user_role(user_id, data.new_role_id, current_admin)

# --- 2. QUẢN LÝ CHỨC VỤ (ROLES) ---

@router.get("/roles", response_model=List[RoleResponse])
def get_all_roles(
    service: AdminManagementService = Depends(get_management_service),
    current_admin: Users = Depends(get_current_admin)
):
    """Lấy danh sách tất cả chức vụ để đổ vào Dropdown trên giao diện"""
    return service.list_roles()

@router.post("/roles", response_model=RoleResponse)
def create_role(
    data: RoleCreateRequest,
    service: AdminManagementService = Depends(get_management_service),
    current_admin: Users = Depends(get_current_admin)
):
    """Tạo thêm chức vụ mới cho hệ thống"""
    return service.add_new_role(data, current_admin.id)

# --- 3. NHẬT KÝ HỆ THỐNG (AUDIT LOGS) ---

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_system_audit_logs(
    limit: int = Query(50),
    service: AdminManagementService = Depends(get_management_service),
    current_admin: Users = Depends(get_current_admin)
):
    """Lấy lịch sử các thao tác quản trị viên đã thực hiện"""
    logs = service.get_audit_logs(limit)
    
    # Map dữ liệu sang Schema để hiển thị tên Admin thay vì ID
    result = []
    for log in logs:
        result.append(AuditLogResponse(
            id=log.id,
            admin_name=log.admin.full_name if log.admin else "Unknown",
            action=log.action,
            target_id=log.target_id,
            details=log.details,
            created_at=log.created_at
        ))
    return result