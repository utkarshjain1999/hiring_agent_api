from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from app.auth.jwt_handler import create_access_token
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM
from app.schemas.users import (
    LoginRequest, RegisterRequest, PasswordSetupRequest, PasswordSetupResponse,
    ResetPasswordRequest, ResetPasswordResponse, ResetPasswordConfirmRequest,
    ResetPasswordConfirmResponse
)
from app.models.users import User
from app.database import get_db
from app.services.email_service import (
    verify_password_setup_token, verify_reset_password_token,
    generate_reset_password_token, send_reset_password_email,
    generate_password_setup_token, send_password_setup_email
)
from app.crud.users import get_user_by_email, update_user_password
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import jwt
import logging

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

class TestUserCreate(BaseModel):
    email: EmailStr
    name: str = "Test User"
    phone_number: str = "+1234567890"
    role: str = "candidate"

class PasswordRequest(BaseModel):
    token: str
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")

class PasswordResponse(BaseModel):
    message: str
    email: str

class RequestPasswordResetRequest(BaseModel):
    email: EmailStr

class RequestPasswordResetResponse(BaseModel):
    message: str
    email: str

@router.post("/test-create-user")
def test_create_user(user_data: TestUserCreate, db: Session = Depends(get_db)):
    """Test endpoint to create a user and trigger the email"""
    try:
        # Create a test user with provided email
        test_user = User(
            email=user_data.email,
            name=user_data.name,
            phone_number=user_data.phone_number,
            role=user_data.role
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        return {"message": "Test user created successfully", "user": test_user.email}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create test user: {str(e)}"
        )

@router.post("/login")
def login_user(login: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not bcrypt.verify(login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"sub": user.email, "role": user.role}
    token = create_access_token(token_data)
    return {
        "token": token,
        "name": user.name,
        "role": user.role,
        "userId": user.id
    }

@router.post("/register")
def register_user(register: RegisterRequest, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == register.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if phone number already exists
    existing_phone = db.query(User).filter(User.phone_number == register.phone_number).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    # If role is provided, validate it
    if register.role and register.role not in ["admin", "hr", "interviewer", "company_representative", "candidate"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    hashed_password = bcrypt.hash(register.password)
    new_user = User(
        email=register.email,
        name=register.name,
        phone_number=register.phone_number,
        hashed_password=hashed_password,
        role=register.role or "candidate"  # Use provided role or default to "candidate"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token_data = {"sub": new_user.email, "role": new_user.role}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/reset-password", response_model=PasswordResponse)
def handle_password(request: PasswordRequest, db: Session = Depends(get_db)):
    """
    Unified endpoint for both password setup and reset.
    The type of operation (setup/reset) is determined from the token.
    """
    # Validate passwords match
    try:
        request.validate_passwords_match()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Verify token and get email and type
    try:
        payload = jwt.decode(request.token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("type")
        
        if not email or token_type not in ["password_setup", "password_reset"]:
            raise HTTPException(status_code=400, detail="Invalid token")
            
        # Get user
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate based on token type
        if token_type == "password_setup":
            if not user.password_setup_required:
                raise HTTPException(status_code=400, detail="Password already set")
        else:  # password_reset
            if user.password_setup_required:
                raise HTTPException(
                    status_code=400,
                    detail="This account has not set up a password yet. Please use the initial password setup link."
                )
        
        # Hash and update password
        hashed_password = pwd_context.hash(request.password)
        update_user_password(db, user, hashed_password)
        
        # Update user fields
        if token_type == "password_setup":
            user.password_setup_required = False
            user.password_setup_token_used = True
        
        user.password_last_changed = datetime.utcnow()
        db.commit()
        
        return PasswordResponse(
            message=f"Password {token_type.replace('password_', '')} successfully",
            email=email
        )
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

@router.post("/verify-email", response_model=RequestPasswordResetResponse)
def request_password_reset(request: RequestPasswordResetRequest, db: Session = Depends(get_db)):
    """
    Endpoint to request a password setup/reset link.
    Sends an email with a setup/reset link if the email exists in the system.
    """
    # Check if user exists
    user = get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="No account found with this email address"
        )
    
    try:
        # Generate appropriate token based on whether user has a password set
        if user.password_setup_required:
            logger.info(f"Generating password setup token for {request.email}")
            token = generate_password_setup_token(request.email)
            logger.info(f"Sending password setup email to {request.email}")
            send_password_setup_email(request.email, token)
        else:
            logger.info(f"Generating password reset token for {request.email}")
            token = generate_reset_password_token(request.email)
            logger.info(f"Sending password reset email to {request.email}")
            send_reset_password_email(request.email, token)
        
        return RequestPasswordResetResponse(
            message="If an account exists with this email, you will receive a password reset link shortly.",
            email=request.email
        )
    except Exception as e:
        logger.error(f"Error in verify-email endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )