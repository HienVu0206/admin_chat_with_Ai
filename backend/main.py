from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import admin,dashboard

app = FastAPI(title="Fresher Chat Admin Backend")

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

@app.get("/")
def read_root():
    return {"message": "Backend Admin đang chạy ngon lành!"}