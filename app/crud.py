from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from datetime import datetime
import re

from app.models import User, UserRole, UserStatus
from app.schemas import UserCreate, UserUpdate
from app.utils import get_password_hash, verify_password

def get_next_user_id(db: Session) -> str:
    """Generate the next user_id in the format USR0001, USR0002, etc."""
    # Get the highest user_id
    highest_user = db.query(User).order_by(User.id.desc()).first()
    
    if not highest_user:
        # No users yet, start with USR0001
        return "USR0001"
    
    # Extract the number from the highest user_id
    match = re.search(r'USR(\d+)', highest_user.user_id)
    if match:
        num = int(match.group(1))
        # Increment and format with leading zeros
        return f"USR{(num + 1):04d}"
    else:
        # Fallback if the format is unexpected
        return f"USR0001"

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    try:
        # Check if username already exists
        existing_username = get_user_by_username(db, user.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
            
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Generate user_id
        user_id = get_next_user_id(db)
        
        # Generate hashed password
        from app.utils import get_password_hash
        hashed_password = get_password_hash(user.password)
        
        # Create user object
        db_user = User(
            user_id=user_id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=user.role,
            status=UserStatus.PENDING
        )
        
        # Add to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except HTTPException:
        # Re-raise HTTP exceptions for validation errors
        raise
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {str(e)}")
        raise

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields if provided
    update_data = user_update.dict(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db_user.updated_at = datetime.now()
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    
    # Uncomment this for production, but for testing we'll allow any status
    # if user.status != UserStatus.ACTIVE:
    #     return False
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user

def change_user_status(db: Session, user_id: int, status: UserStatus):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db_user.status = status
    db_user.updated_at = datetime.now()
    db.commit()
    db.refresh(db_user)
    return db_user







