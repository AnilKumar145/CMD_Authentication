from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models import UserRole, UserStatus

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.PATIENT  # Default role is patient

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    status: Optional[UserStatus] = None
    disabled: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login: datetime | None = None

    class Config:
        from_attributes = True  # This replaces orm_mode in Pydantic v2

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None




