from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Import the UserRole and UserStatus from models if they're defined there
from app.models import UserRole, UserStatus
# Enum definitions (if not already defined)
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"
    STAFF = "STAFF"

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"

# User response schema with all necessary fields
class UserResponse(BaseModel):
    id: int
    user_id: str
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    status: UserStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    disabled: Optional[bool] = None
    
    class Config:
        from_attributes = True  # For Pydantic v2
        populate_by_name = True  # For Pydantic v2

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.PATIENT  # Default to PATIENT

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    disabled: Optional[bool] = None
    
    class Config:
        from_attributes = True





