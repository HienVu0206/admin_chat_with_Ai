from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import admin, dashboard, admin_manager, admin_chat

# --- BỔ SUNG 1: Import các thư viện cho Cronjob và Database ---
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.cron_dashboard import calculate_daily_stats
from app.core.database import SessionLocal # Lưu ý: Bạn kiểm tra lại đường dẫn import SessionLocal cho chuẩn với project nhé

# --- BỔ SUNG 2: Hàm chạy tác vụ tính toán ---
def job_run_daily_stats():
    db = SessionLocal() # Mở kết nối database
    try:
        calculate_daily_stats(db)
    finally:
        db.close() # Đóng kết nối khi tính xong để giải phóng bộ nhớ

# --- BỔ SUNG 3: Quản lý vòng đời ứng dụng (Lifespan) để Bật/Tắt Cronjob ---
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # KHI BẬT SERVER: Khởi động Scheduler
#     scheduler = BackgroundScheduler()
#     # Cài đặt lịch: Chạy vào lúc 23:59 mỗi ngày
#     scheduler.add_job(job_run_daily_stats, 'cron', hour=9, minute=10)
#     scheduler.start()
#     print("🕒 Đã bật hệ thống Cronjob: Tính toán thống kê vào 09:01 mỗi ngày!")
    
#     yield # Cho phép FastAPI tiếp tục chạy các tiến trình khác
    
#     # KHI TẮT SERVER: Dọn dẹp Scheduler an toàn
#     scheduler.shutdown()
#     print("🛑 Đã tắt an toàn hệ thống Cronjob!")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # KHI BẬT SERVER: Khởi động Scheduler
    scheduler = BackgroundScheduler()
    
    # Cài đặt lịch: VD chạy 1 tiếng 1 lần (ở phút thứ 0 của mỗi giờ)
    # scheduler.add_job(job_run_daily_stats, 'cron', minute=0)

    # Chạy 10 phút 1 lần
    scheduler.add_job(job_run_daily_stats, 'cron', minute='*/10')
    # Nếu muốn chạy cố định 09:10 mỗi ngày thì mở comment dòng dưới và xóa dòng trên:
    # scheduler.add_job(job_run_daily_stats, 'cron', hour=9, minute=10)
    
    scheduler.start()
    print("🕒 Đã bật hệ thống Cronjob: Tính toán thống kê Dashboard tự động!")
    
    yield 
    
    # KHI TẮT SERVER: Dọn dẹp Scheduler an toàn
    scheduler.shutdown()
    print("🛑 Đã tắt an toàn hệ thống Cronjob!")

# --- SỬA NHẸ: Gắn lifespan vào FastAPI ---
app = FastAPI(title="Fresher Chat Admin Backend", lifespan=lifespan)

# Cấu hình CORS (Để VueJS gọi được)
origins = [
    "http://localhost:5173", # Cổng mặc định của Vite/Vue
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký Router
app.include_router(admin.router)
app.include_router(dashboard.router)
app.include_router(admin_manager.router)
app.include_router(admin_chat.router)

@app.get("/")
def read_root():
    return {"message": "Backend Admin đang chạy ngon lành!"}