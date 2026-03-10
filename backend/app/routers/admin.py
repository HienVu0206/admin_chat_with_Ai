from fastapi import APIRouter, Depends, Body, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin, verify_refresh_token
from app.models.models import Users
from app.models.models import Users, BanLogs, AdminActionLogs
from app.services.admin_service import AdminService, AdminManagementService
from app.services.role_service import RoleService
from app.schemas.admin_schema import (
    TokenResponse, BanUserRequest, ChangeRoleRequest, 
    UserAdminResponse, AuditLogResponse
)
from app.schemas.role import RoleResponse, RoleUpdateRequest

router = APIRouter(prefix="/admin", tags=["Admin Management"])

# --- Dependencies ---
def get_admin_service(db: Session = Depends(get_db)):
    return AdminService(db)

def get_management_service(db: Session = Depends(get_db)):
    return AdminManagementService(db)

def get_role_service(db: Session = Depends(get_db)):
    return RoleService(db)

# --- Routes ---

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), service: AdminService = Depends(get_admin_service)):
    return service.login_admin(form_data.username, form_data.password)

@router.get("/users", response_model=List[UserAdminResponse])
def list_users(
    role_id: int = Query(None), search: str = Query(None),
    service: AdminManagementService = Depends(get_management_service),
    admin: Users = Depends(get_current_admin)
):
    return service.list_users(role_id, search)

@router.patch("/users/{user_id}/ban")
def ban_user(
    user_id: int, data: BanUserRequest,
    service: AdminManagementService = Depends(get_management_service),
    admin: Users = Depends(get_current_admin)
):
    return service.ban_user(user_id, data.reason, admin.id)

@router.patch("/users/{user_id}/unban")
def unban_user(
    user_id: int,
    service: AdminManagementService = Depends(get_management_service),
    admin: Users = Depends(get_current_admin)
):
    return service.unban_user(user_id, admin.id)

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_logs(service: AdminManagementService = Depends(get_management_service), admin: Users = Depends(get_current_admin)):
    logs = service.get_audit_logs()
    return [
        AuditLogResponse(
            id=l.id, admin_name=l.admin.full_name if l.admin else "System",
            action=l.action, target_id=l.target_id, details=l.details, created_at=l.created_at
        ) for l in logs
    ]

@router.put("/roles/{role_id}", response_model=RoleResponse)
def edit_role(
    role_id: int,
    data: RoleUpdateRequest,
    service: AdminManagementService = Depends(get_management_service),
    current_admin: Users = Depends(get_current_admin)
):
    """Cập nhật thông tin chức vụ (Chỉ dành cho Admin)"""
    return service.update_role(role_id, data, current_admin.id)

@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    service: AdminManagementService = Depends(get_management_service),
    current_admin: Users = Depends(get_current_admin)
):
    """Xóa chức vụ ra khỏi hệ thống"""
    return service.delete_role(role_id, current_admin.id)