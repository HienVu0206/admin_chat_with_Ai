from sqlalchemy.orm import Session
from app.models.models import Users, Roles

class AdminRepository:
    def get_admin_by_email(self, db: Session, email: str):
        # Lấy user có role là 'admin' và status là 'active'
        return db.query(Users).join(Roles).filter(
            Users.email == email,
            Users.status == 'active',
            Roles.name == 'admin' 
        ).first()