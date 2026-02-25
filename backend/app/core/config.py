# --- app/core/config.py ---
class Settings:
    SECRET_KEY: str = "your_super_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Thêm cấu hình Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_EXPIRE_SECONDS: int = 300  # Lưu cache trong 5 phút

settings = Settings()