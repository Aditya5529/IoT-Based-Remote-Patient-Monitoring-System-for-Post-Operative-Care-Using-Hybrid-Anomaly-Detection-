import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RPM Vital Collection"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "supersecretkeyForDevelopmentOnly")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    DATABASE_URL: str
    REDIS_URL: str
    
    # IoT Settings
    THINGSPEAK_CHANNEL_ID: str = os.environ.get("THINGSPEAK_CHANNEL_ID", "")
    THINGSPEAK_READ_API_KEY: str = os.environ.get("THINGSPEAK_READ_API_KEY", "")
    IOT_DEVICE_SECRET: str = os.environ.get("IOT_DEVICE_SECRET", "secret123")

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
