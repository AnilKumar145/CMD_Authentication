from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://cmd_user:GIxYa0Fx753DAD47VNY9pH8Dpuq3Le7l@dpg-d0p91j8dl3ps73aipd3g-a/cmd")
    
    # Auth settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY_HERE")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Service URLs
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "https://healthcare-auth-service.onrender.com")
    DOCTOR_SERVICE_URL: str = os.getenv("DOCTOR_SERVICE_URL", "https://healthcare-doctor-service.onrender.com")
    PATIENT_SERVICE_URL: str = os.getenv("PATIENT_SERVICE_URL", "https://healthcare-patient-service.onrender.com")
    APPOINTMENT_SERVICE_URL: str = os.getenv("APPOINTMENT_SERVICE_URL", "https://healthcare-appointment-service.onrender.com")
    FACILITY_SERVICE_URL: str = os.getenv("FACILITY_SERVICE_URL", "https://healthcare-facility-service.onrender.com")
    ASSETS_SERVICE_URL: str = os.getenv("ASSETS_SERVICE_URL", "https://healthcare-assets-service.onrender.com")
    
    # Email settings
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "anilkumarsala58@gmail.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "Welcome@1")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "anilkumarsala2003@gmail.com")
    
    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://healthcare-frontend.onrender.com")

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()


