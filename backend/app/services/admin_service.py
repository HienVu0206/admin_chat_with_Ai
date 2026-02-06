from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.repositories.admin_repo import AdminRepository
from app.services.auth_service import AuthService
from app.schemas.admin_schema import TokenResponse

class AdminService:
    def __init__(self):
        self.repo = AdminRepository()
        self.auth_service = AuthService()

    def login_admin(self, db: Session, email: str, password: str) -> TokenResponse:
        # 1. Tìm user
        user = self.repo.get_admin_by_email(db, email)
        
        if not user:
             raise HTTPException(status_code=401, detail="Tài khoản không tồn tại hoặc không phải Admin")

        # 2. Check Pass (Hỗ trợ cả pass thường 123456 và pass mã hóa)
        is_valid = False
        if user.password == password: 
            is_valid = True
        elif verify_password(password, user.password):
            is_valid = True
            
        if not is_valid:
            raise HTTPException(status_code=401, detail="Mật khẩu không đúng")
        
        # 3. Tạo Token từ AuthService
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