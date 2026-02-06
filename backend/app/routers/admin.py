from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.admin_service import AdminService
from app.schemas.admin_schema import LoginRequest, TokenResponse

router = APIRouter(prefix="/admin", tags=["Admin Auth"])

@router.post("/login", response_model=TokenResponse)
async def admin_login(data: LoginRequest, db: Session = Depends(get_db)):
    service = AdminService()
    return service.login_admin(db, data.email, data.password)