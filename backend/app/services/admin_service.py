from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.models.models import Users, Roles, AdminActionLogs, BanLogs
from app.core.security import verify_password
from app.services.auth_service import AuthService
from app.repositories.admin_repo import AdminRepository

# --- SỬA IMPORT TẠI ĐÂY ---
from app.schemas.admin_schema import (
    TokenResponse, 
    UserAdminResponse, 
    RoleResponse, 
    RoleCreateRequest
)
from app.schemas.role import RoleUpdateRequest  # Import từ đúng file role.py
# ---------------------------

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

    # --- QUẢN LÝ BẢNG ROLES ---

    def list_roles(self) -> List[RoleResponse]:
        """Lấy toàn bộ danh sách chức vụ ĐANG HOẠT ĐỘNG (chưa bị xóa)"""
        # Thêm điều kiện is_active == True để loại bỏ các role đã xóa mềm
        return self.db.query(Roles).filter(Roles.is_active == True).all()

    def add_new_role(self, data: RoleCreateRequest, admin_id: int):
        """Thêm chức vụ mới vào bảng Roles"""
        new_role = Roles(name=data.name, description=data.description)
        self.db.add(new_role)
        self.db.commit()
        self.db.refresh(new_role)

        self.log_action(admin_id, "CREATE_ROLE", new_role.id, f"Tạo role mới: {new_role.name}")
        return new_role

    def update_role(self, role_id: int, data: RoleUpdateRequest, admin_id: int):
        """Cập nhật thông tin chức vụ"""
        # 1. Tìm role cần sửa (chỉ sửa những role chưa bị xóa)
        role = self.db.query(Roles).filter(Roles.id == role_id, Roles.is_active == True).first()
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy chức vụ này hoặc đã bị xóa")
        
        # 2. Kiểm tra xem tên mới có bị trùng với role khác không
        if data.name != role.name:
            existing_role = self.db.query(Roles).filter(Roles.name == data.name).first()
            if existing_role:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên chức vụ này đã tồn tại")
        
        # 3. Cập nhật và lưu
        old_name = role.name
        role.name = data.name
        role.description = data.description
        
        self.db.commit()
        self.db.refresh(role)
        
        # 4. Ghi log
        self.log_action(admin_id, "UPDATE_ROLE", role.id, f"Cập nhật role từ '{old_name}' thành '{role.name}'")
        return role

    def delete_role(self, role_id: int, admin_id: int):
        """XÓA MỀM (Soft Delete) chức vụ"""
        # 1. Tìm role cần xóa
        role = self.db.query(Roles).filter(Roles.id == role_id).first()
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy chức vụ này")
        
        # Kiểm tra xem role này đã bị xóa trước đó chưa
        if not role.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chức vụ này đã bị xóa từ trước rồi")
        
        # 2. Ràng buộc quan trọng: Không cho xóa nếu đang có User giữ Role này
        if self.db.query(Users).filter(Users.role_id == role_id).count() > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Không thể xóa Role đang có người sử dụng. Hãy chuyển họ sang Role khác trước."
            )
            
        # 3. Tiến hành XÓA MỀM thay vì hard delete
        role_name = role.name
        role.is_active = False # Chỉ cập nhật trạng thái
        
        self.db.commit()
        
        # 4. Ghi log
        self.log_action(admin_id, "SOFT_DELETE_ROLE", role_id, f"Đã xóa mềm role: {role_name}")
        return {"status": "success", "message": f"Đã xóa chức vụ {role_name} thành công"}


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

    def ban_user(self, user_id: int, reason: str, admin_id: int):
        user = self.db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.status = 'banned'

        # Ghi vào bảng BanLogs
        new_ban_log = BanLogs( 
            user_id=user_id,
            banned_by=admin_id,
            reason=reason
        )
        self.db.add(new_ban_log)

        # Ghi vào bảng AdminActionLogs
        new_action_log = AdminActionLogs(
            admin_id=admin_id,
            action="BAN_USER",
            target_id=user_id,
            details=f"Banned user: {user.email}. Reason: {reason}"
        )
        self.db.add(new_action_log)

        self.db.commit()
        return {"message": "User has been banned successfully"}

    def unban_user(self, user_id: int, admin_id: int):
        # 1. Tìm user cần unban
        user = self.db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

        if user.status == 'active':
            raise HTTPException(status_code=400, detail="Người dùng này đang hoạt động, không thể mở khóa")

        # 2. Cập nhật trạng thái user thành 'active'
        user.status = 'active'
        
        # 3. Ghi log hành động của admin
        new_log = AdminActionLogs(
            admin_id=admin_id,
            action="UNBAN_USER",
            target_id=user_id,
            details=f"Đã mở khóa tài khoản người dùng ID {user_id}"
        )
        self.db.add(new_log)

        # 4. Lưu vào database
        self.db.commit()
        self.db.refresh(user)

        return {"message": "Đã mở khóa người dùng thành công", "user_id": user.id, "status": user.status}

    def change_user_role(self, target_user_id: int, new_role_id: int, current_admin: Users):
        """Thay đổi chức vụ người dùng và ghi log"""
        target_user = self.db.query(Users).filter(Users.id == target_user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

        # 1. Kiểm tra xem role mới có hợp lệ và CÒN HOẠT ĐỘNG không
        new_role = self.db.query(Roles).filter(Roles.id == new_role_id, Roles.is_active == True).first()
        if not new_role:
            raise HTTPException(status_code=400, detail="Quyền (Role) không tồn tại hoặc đã bị khóa")

        # 2. CHẶN KHÔNG CHO CẤP QUYỀN ADMIN (Thêm đoạn này)
        if new_role.name.lower() in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Bạn không có quyền cấp chức vụ Admin cho người dùng khác."
            )

        # 3. (Bảo mật bổ sung) Chặn Admin thay đổi quyền của một Admin khác để tránh phá hoại nội bộ
        if target_user.role and target_user.role.name.lower() in ["admin", "super_admin"]:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Bạn không thể hạ quyền hoặc thay đổi chức vụ của một quản trị viên khác."
            )

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

    # --- NHẬT KÝ ---

    def get_audit_logs(self, limit: int = 50) -> List[AdminActionLogs]:
        """Lấy danh sách nhật ký hoạt động mới nhất"""
        return self.db.query(AdminActionLogs)\
            .order_by(AdminActionLogs.created_at.desc())\
            .limit(limit)\
            .all()