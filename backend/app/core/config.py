class Settings:
    SECRET_KEY: str = "your_super_secret_key_change_this_immediately"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60         # 1 Tiếng
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7            # 7 Ngày

settings = Settings()