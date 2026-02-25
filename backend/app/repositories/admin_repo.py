from typing import Optional
from sqlalchemy.orm import Session

# Đảm bảo đường dẫn import models đúng với dự án của bạn
from app.models.models import Users, Roles

class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_admin_by_email(self, email: str) -> Optional[Users]:
        """Lấy user có role là 'admin' và status là 'active'"""
        return self.db.query(Users).join(Roles).filter(
            Users.email == email,
            Users.status == 'active',
            Roles.name == 'admin' 
        ).first()