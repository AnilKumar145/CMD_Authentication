import traceback

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from jose import JWTError, jwt

from app.database import engine, get_db, Base
from app.models import User, UserRole, UserStatus
from app.schemas import UserCreate, UserResponse, UserUpdate, Token, TokenData
from app.crud import (
    create_user, get_user_by_username, get_users, 
    update_user, authenticate_user, change_user_status
)
from app.utils import (
    create_access_token, send_verification_email, 
    send_password_reset_email
)
from app.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auth Microservice",
    description="Handles authentication and authorization for the healthcare system",
    version="1.0.0"
)

# Add global exception handler to prevent credential leakage
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Get the full traceback
    error_details = traceback.format_exc()
    # Log the detailed error
    print(f"Global exception: {str(exc)}")
    print(f"Traceback: {error_details}")
    # Return a safe error message
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://healthcare-frontend.onrender.com",
        "http://localhost:3000"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency for getting current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=payload.get("role"))
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Dependency for admin-only endpoints
async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convert enum to string for JSON serialization
    access_token, expires_in = create_access_token(
        data={"sub": user.username, "role": str(user.role.value)}
    )
    
    # Convert SQLAlchemy model to Pydantic model
    user_response = UserResponse.model_validate(user.__dict__)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": user_response
    }

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        # Check if username already exists
        existing_user = get_user_by_username(db, user.username)
        if existing_user:
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
        
        # Only allow patient self-registration
        if user.role != UserRole.PATIENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only patient registration is allowed"
            )
        
        db_user = create_user(db, user)
        
        # Automatically activate the user for testing
        db_user.status = UserStatus.ACTIVE
        db.commit()
        db.refresh(db_user)
        
        # Convert SQLAlchemy model to Pydantic model
        return UserResponse.model_validate(db_user.__dict__)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error
        print(f"Registration error: {str(e)}")
        # Return a more helpful error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed. Please try again."
        )

@app.post("/admin/create-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_non_patient_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        # Log the incoming request data
        print(f"Creating admin user: {user.dict()}")
        
        # Create the user (validation happens in crud.py)
        db_user = create_user(db, user)
        
        # Automatically activate the user
        db_user.status = UserStatus.ACTIVE
        db.commit()
        db.refresh(db_user)
        
        # Log successful creation
        print(f"User created successfully: {db_user.username}")
        
        # Convert SQLAlchemy model to Pydantic model
        user_dict = {
            "id": db_user.id,
            "user_id": db_user.user_id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "role": db_user.role,
            "status": db_user.status,
            "created_at": db_user.created_at,
            "updated_at": db_user.updated_at,
            "disabled": db_user.disabled
        }
        return UserResponse(**user_dict)
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions
        raise http_exc
    except Exception as e:
        # Log the detailed error
        print(f"Admin user creation error: {str(e)}")
        # Return a generic error message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user. Please try again later."
        )

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user.__dict__)

@app.get("/users", response_model=List[UserResponse])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admins can list all users
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view all users"
        )
    
    users = get_users(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(user.__dict__) for user in users]









