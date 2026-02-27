from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.models.models import Users, Roles, AdminActionLogs
from app.core.security import verify_password
from app.services.auth_service import AuthService
from app.repositories.admin_repo import AdminRepository
from app.schemas.admin_schema import (
    TokenResponse, 
    UserAdminResponse, 
    RoleResponse, 
    RoleCreateRequest
)

class AdminService:
    def __init__(self, db: Session):
        self.repo = AdminRepository(db)
        self.auth_service = AuthService()

    def login_admin(self, email: str, password: str) -> TokenResponse:
        """Xử lý đăng nhập cho quản trị viên"""
        user = self.repo.get_admin_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Tài khoản không tồn tại hoặc không phải Admin"
            )

        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Mật khẩu không đúng"
            )
        
        access_token = self.auth_service.create_access_token(
            data={"sub": str(user.id), "role": user.role.name}
        )
        refresh_token = self.auth_service.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            role=user.role.name
        )

class AdminManagementService:
    def __init__(self, db: Session):
        self.db = db

    def log_action(self, admin_id: int, action: str, target_id: int = None, details: str = None):
        """Ghi nhật ký hoạt động của Admin vào database"""
        log = AdminActionLogs(
            admin_id=admin_id,
            action=action,
            target_id=target_id,
            details=details
        )
        self.db.add(log)
        self.db.commit()

    # --- QUẢN LÝ NGƯỜI DÙNG & PHÂN QUYỀN ---

    def list_users(self, role_id: Optional[int] = None, search: Optional[str] = None) -> List[UserAdminResponse]:
        """Lấy danh sách người dùng kèm bộ lọc theo Role và tìm kiếm tên/email"""
        query = self.db.query(Users).options(joinedload(Users.role))

        if role_id:
            query = query.filter(Users.role_id == role_id)
        
        if search:
            query = query.filter(
                or_(
                    Users.full_name.ilike(f"%{search}%"),
                    Users.email.ilike(f"%{search}%")
                )
            )
        
        users = query.all()
        return [
            UserAdminResponse(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                status=u.status,
                role_id=u.role_id,
                role_name=u.role.name,
                created_at=u.created_at
            ) for u in users
        ]

    def change_user_role(self, target_user_id: int, new_role_id: int, current_admin: Users):
        """Thay đổi chức vụ người dùng và ghi log"""
        target_user = self.db.query(Users).filter(Users.id == target_user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

        new_role = self.db.query(Roles).filter(Roles.id == new_role_id).first()
        if not new_role:
            raise HTTPException(status_code=400, detail="Quyền (Role) không hợp lệ")

        old_role_name = target_user.role.name
        target_user.role_id = new_role_id
        self.db.commit()

        details = f"Đổi quyền từ '{old_role_name}' sang '{new_role.name}'"
        self.log_action(
            admin_id=current_admin.id, 
            action="CHANGE_ROLE", 
            target_id=target_user.id, 
            details=details
        )
        return {"status": "success", "message": f"Đã cập nhật quyền thành {new_role.name}"}

    # --- QUẢN LÝ BẢNG ROLES ---

    def list_roles(self) -> List[RoleResponse]:
        """Lấy toàn bộ danh sách chức vụ có trong hệ thống"""
        return self.db.query(Roles).all()

    def add_new_role(self, data: RoleCreateRequest, admin_id: int):
        """Thêm chức vụ mới vào bảng Roles"""
        new_role = Roles(name=data.name, description=data.description)
        self.db.add(new_role)
        self.db.commit()
        self.db.refresh(new_role)

        self.log_action(admin_id, "CREATE_ROLE", new_role.id, f"Tạo role mới: {new_role.name}")
        return new_role

    def delete_role(self, role_id: int, admin_id: int):
        """Xóa hoặc ẩn role (Lưu ý: Chỉ xóa được nếu không có user nào đang giữ role này)"""
        role = self.db.query(Roles).filter(Roles.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role không tồn tại")
        
        # Kiểm tra xem có user nào đang sử dụng role này không
        user_count = self.db.query(Users).filter(Users.role_id == role_id).count()
        if user_count > 0:
            raise HTTPException(
                status_code=400, 
                detail="Không thể xóa Role đang có người sử dụng. Hãy chuyển họ sang Role khác trước."
            )

        role_name = role.name
        self.db.delete(role)
        self.db.commit()

        self.log_action(admin_id, "DELETE_ROLE", role_id, f"Đã xóa role: {role_name}")
        return {"message": "Đã xóa chức vụ thành công"}

    # --- NHẬT KÝ ---

    def get_audit_logs(self, limit: int = 50) -> List[AdminActionLogs]:
        """Lấy danh sách nhật ký hoạt động mới nhất"""
        return self.db.query(AdminActionLogs)\
            .order_by(AdminActionLogs.created_at.desc())\
            .limit(limit)\
            .all()