from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
from app.models.models import Users, Conversations, Messages, DashboardDailyStats # Cập nhật đường dẫn import model của bạn

def calculate_daily_stats(db: Session):
    # Xác định ngày hôm nay và mốc thời gian đầu ngày/cuối ngày
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    
    print(f"Bắt đầu tổng hợp dữ liệu cho ngày: {today}")

    # 1. Tổng người dùng (tính đến hiện tại)
    total_users = db.query(func.count(Users.id)).scalar() or 0

    # 2. User hoạt động trong 24h qua (Ví dụ: những user có nhắn tin hôm nay)
    # Lấy ra số lượng user_id duy nhất (distinct) có gửi tin nhắn trong ngày
    active_users = db.query(func.count(func.distinct(Conversations.user_id)))\
        .join(Messages, Messages.conversation_id == Conversations.id)\
        .filter(Messages.created_at >= start_of_day).scalar() or 0

    # 3. Số đoạn chat mới tạo trong hôm nay
    new_chats = db.query(func.count(Conversations.id))\
        .filter(Conversations.created_at >= start_of_day).scalar() or 0

    # 4. Tổng tin nhắn toàn hệ thống (tính đến hiện tại)
    total_messages = db.query(func.count(Messages.id)).scalar() or 0

    # 5. Tỷ lệ tin nhắn User / AI trong hôm nay
    messages_today = db.query(Messages.role, func.count(Messages.id))\
        .filter(Messages.created_at >= start_of_day)\
        .group_by(Messages.role).all()
    
    user_msg_count = 0
    ai_bot_msg_count = 0
    
    for role, count in messages_today:
        if role == 'user':
            user_msg_count = count
        elif role == 'ai':
            ai_bot_msg_count = count

    # --- LƯU VÀO DATABASE ---
    
    # Kiểm tra xem hôm nay đã có bản ghi nào chưa (tránh lỗi duplicate PK)
    stat_record = db.query(DashboardDailyStats).filter(DashboardDailyStats.date == today).first()
    
    if not stat_record:
        # Nếu chưa có thì tạo mới
        stat_record = DashboardDailyStats(
            date=today,
            total_users=total_users,
            active_users=active_users,
            new_chats=new_chats,
            total_messages=total_messages,
            user_msg_count=user_msg_count,
            ai_bot_msg_count=ai_bot_msg_count
        )
        db.add(stat_record)
    else:
        # Nếu có rồi thì cập nhật (dành cho trường hợp chạy lại script)
        stat_record.total_users = total_users
        stat_record.active_users = active_users
        stat_record.new_chats = new_chats
        stat_record.total_messages = total_messages
        stat_record.user_msg_count = user_msg_count
        stat_record.ai_bot_msg_count = ai_bot_msg_count

    db.commit()
    print(f"✅ Đã lưu thành công dữ liệu ngày {today} vào bảng DashboardDailyStats!")