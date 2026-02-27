from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.models import Users, Roles

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
    
class AdminManagementRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self, role_id: int = None, search: str = None):
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
        return query.all()

    # --- QUẢN LÝ ROLE ---
    def get_roles(self):
        return self.db.query(Roles).all()

    def create_role(self, name: str, description: str):
        new_role = Roles(name=name, description=description)
        self.db.add(new_role)
        self.db.commit()
        self.db.refresh(new_role)
        return new_role

    def get_role_by_id(self, role_id: int):
        return self.db.query(Roles).filter(Roles.id == role_id).first()