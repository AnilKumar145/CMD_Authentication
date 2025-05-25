# Use absolute imports
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

def send_email(to_email, subject, html_content):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, message.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_verification_email(user_email, verification_token):
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    
    html_content = f"""
    <html>
    <body>
        <h2>Welcome to Healthcare System</h2>
        <p>Please verify your email address by clicking the link below:</p>
        <p><a href="{verification_url}">Verify Email</a></p>
        <p>If you didn't request this, please ignore this email.</p>
    </body>
    </html>
    """
    
    return send_email(
        user_email,
        "Verify Your Email - Healthcare System",
        html_content
    )

def send_password_reset_email(user_email, reset_token):
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    
    html_content = f"""
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>You requested to reset your password. Click the link below to set a new password:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>If you didn't request this, please ignore this email.</p>
    </body>
    </html>
    """
    
    return send_email(
        user_email,
        "Reset Your Password - Healthcare System",
        html_content
    )

