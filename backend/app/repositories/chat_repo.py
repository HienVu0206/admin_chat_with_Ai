from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.models import Conversations, Users

def get_all_conversations_db(db: Session, search: str = None):
    # Dùng DB Query lấy trực tiếp các cột cần thiết từ 2 bảng
    query = db.query(
        Conversations.id,
        Users.full_name.label("user_name"),
        Conversations.title,
        Conversations.created_at,
        Conversations.updated_at
    ).join(Users, Conversations.user_id == Users.id)

    # Nếu có từ khóa search -> Tìm tương đối (ILIKE) theo title hoặc tên user
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Conversations.title.ilike(search_term),
                Users.full_name.ilike(search_term)
            )
        )

    # Sắp xếp chat mới nhất lên đầu
    query = query.order_by(Conversations.created_at.desc())
    
    return query.all()