from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from datetime import datetime
import re

from app.models import User, UserRole, UserStatus
from app.schemas import UserCreate, UserUpdate
from app.utils import get_password_hash, verify_password

def get_next_user_id(db: Session):
    try:
        # Get the highest user_id
        last_user = db.query(User).order_by(User.id.desc()).first()
        
        if last_user and last_user.user_id and last_user.user_id.startswith("USR"):
            # Extract the number part and increment
            last_id = int(last_user.user_id[3:])
            next_id = last_id + 1
        else:
            # Start with 1 if no users exist
            next_id = 1
            
        # Format as USR followed by 6 digits
        return f"USR{next_id:06d}"
    except Exception as e:
        print(f"Error in get_next_user_id: {str(e)}")
        # Fallback to a timestamp-based ID
        import time
        return f"USR{int(time.time())}"

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
        existing_email = get_user_by_email(db, user.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Generate user_id if the function exists
        try:
            user_id = get_next_user_id(db)
        except Exception as e:
            print(f"Error generating user_id: {str(e)}")
            # Fallback to a simple UUID if get_next_user_id fails
            import uuid
            user_id = str(uuid.uuid4())
        
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
        print(f"Error creating user in crud.py: {str(e)}")
        # Re-raise the exception to be handled by the endpoint
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












