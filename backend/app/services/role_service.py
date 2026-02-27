from sqlalchemy.orm import Session
from app.repositories.role_repo import RoleRepository

class RoleService:
    def __init__(self, db: Session):
        self.repo = RoleRepository(db)

    def get_all_roles(self):
        """Xử lý logic lấy danh sách roles"""
        # Hiện tại logic khá đơn giản, chỉ việc gọi xuống Repo
        roles = self.repo.get_all_roles()
        return roles