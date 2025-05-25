from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:Anil@localhost:5432/healthcare_db"
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "anilkumarsala58@gmail.com"  # Update with your actual email
    SMTP_PASSWORD: str = "Welcome@1"  # Update with an app password
    EMAIL_FROM: str = "anilkumarsala2003@gmail.com"  # Update with your actual email
    
    # Frontend URL for email verification
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
