from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
'''
from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
'''
# Database URL from environment variable with fallback
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cmd_user:GIxYa0Fx753DAD47VNY9pH8Dpuq3Le7l@dpg-d0p91j8dl3ps73aipd3g-a/cmd")

# Add SSL mode for Render
if "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

# Create engine with production settings
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

