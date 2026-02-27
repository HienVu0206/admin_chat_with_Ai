from sqlalchemy.orm import Session
#Import model Roles của bạn
from app.models.models import Roles 

class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_roles(self):
        """Lấy toàn bộ danh sách roles từ database"""
        return self.db.query(Roles).all()