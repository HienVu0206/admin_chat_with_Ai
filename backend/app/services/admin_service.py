from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.repositories.admin_repo import AdminRepository
from app.services.auth_service import AuthService
from app.schemas.admin_schema import TokenResponse

class AdminService:
    # 1. Nhận db ngay từ lúc khởi tạo Service (Dependency Injection)
    def __init__(self, db: Session):
        self.repo = AdminRepository(db)
        self.auth_service = AuthService()

    # 2. Xóa tham số db ở đây, chỉ cần email và password
    def login_admin(self, email: str, password: str) -> TokenResponse:
        # Tìm user
        user = self.repo.get_admin_by_email(email)
        
        if not user:
             raise HTTPException(status_code=401, detail="Tài khoản không tồn tại hoặc không phải Admin")

        # Kiểm tra mật khẩu (Viết gọn lại cực kỳ sạch sẽ)
        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Mật khẩu không đúng")
        
        # Tạo Token
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