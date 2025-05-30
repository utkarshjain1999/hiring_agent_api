from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta
from typing import Optional
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.crud.users import check_token_used
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug environment loading
current_dir = os.getcwd()
env_path = os.path.join(current_dir, '.env')
logger.info(f"Current working directory: {current_dir}")
logger.info(f"Looking for .env file at: {env_path}")
logger.info(f".env file exists: {os.path.exists(env_path)}")

# Load environment variables
load_dotenv(env_path)

# Email settings from environment variables
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))  # Default to 587 if not set
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_TOKEN = os.getenv("SMTP_TOKEN")
FRONTEND_URL = os.getenv("FRONTEND_URL")

# Log environment variable status (without sensitive data)
logger.info("Checking SMTP configuration:")
logger.info(f"SMTP_HOST: {SMTP_HOST}")
logger.info(f"SMTP_PORT: {SMTP_PORT}")
logger.info(f"SMTP_USERNAME: {SMTP_USERNAME}")
logger.info(f"SMTP_TOKEN: {'Set' if SMTP_TOKEN else 'Not set'}")
logger.info(f"FRONTEND_URL: {FRONTEND_URL}")

# Log raw environment variables (for debugging)
logger.info("Raw environment variables:")
logger.info(f"SMTP_USERNAME value: {os.getenv('SMTP_USERNAME')}")
logger.info(f"SMTP_TOKEN value: {'Set' if os.getenv('SMTP_TOKEN') else 'Not set'}")

def generate_password_setup_token(email: str) -> str:
    """Generate a JWT token for password setup that expires in 24 hours"""
    expiration = datetime.utcnow() + timedelta(hours=24)
    token_data = {
        "sub": email,
        "exp": expiration,
        "type": "password_setup"
    }
    return jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def generate_reset_password_token(email: str) -> str:
    """Generate a JWT token for password reset that expires in 1 hour"""
    expiration = datetime.utcnow() + timedelta(hours=1)
    token_data = {
        "sub": email,
        "exp": expiration,
        "type": "password_reset"
    }
    return jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_password_setup_token(token: str, db: Session) -> Optional[str]:
    """Verify the password setup token and return the email if valid"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "password_setup":
            return None
        
        email = payload.get("sub")
        # Check if token has already been used
        if check_token_used(db, email):
            raise HTTPException(
                status_code=400,
                detail="This password setup link has already been used. Please request a new one."
            )
        
        return email
    except jwt.PyJWTError:
        return None

def verify_reset_password_token(token: str, db: Session) -> Optional[str]:
    """Verify the reset password token and return the email if valid"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        
        email = payload.get("sub")
        # Check if token has already been used
        if check_token_used(db, email):
            raise HTTPException(
                status_code=400,
                detail="This password reset link has already been used. Please request a new one."
            )
        
        return email
    except jwt.PyJWTError:
        return None

def send_password_setup_email(email: str, token: str):
    """Send password setup email with the token link"""
    if not all([SMTP_USERNAME, SMTP_TOKEN]):
        error_msg = "SMTP credentials not properly configured"
        logger.error(error_msg)
        logger.error(f"SMTP_USERNAME: {'Set' if SMTP_USERNAME else 'Not set'}")
        logger.error(f"SMTP_TOKEN: {'Set' if SMTP_TOKEN else 'Not set'}")
        raise HTTPException(status_code=500, detail=error_msg)

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = "Set Up Your Password"

        # Create the body of the message
        password_link = f"{FRONTEND_URL}/reset-password?token={token}"
        body = f"""
        Welcome to our platform!
        
        Please click the link below to set up your password:
        {password_link}
        
        This link will expire in 24 hours and can only be used once.
        
        If you didn't request this, please ignore this email.
        """
        
        msg.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server and send email
        logger.info(f"Attempting to connect to SMTP server: {SMTP_HOST}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.set_debuglevel(1)  # Enable debug output
            logger.info("Starting TLS connection")
            server.starttls()
            
            logger.info("Attempting SMTP login")
            server.login(SMTP_USERNAME, SMTP_TOKEN)
            
            logger.info(f"Sending email to {email}")
            server.send_message(msg)
            logger.info("Email sent successfully")
            
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication failed: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error occurred: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

def send_reset_password_email(email: str, token: str):
    """Send password reset email with the token link"""
    logger.info(f"Starting send_reset_password_email for {email}")
    
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_TOKEN]):
        error_msg = "SMTP credentials not properly configured"
        logger.error(error_msg)
        logger.error(f"SMTP_HOST: {SMTP_HOST}")
        logger.error(f"SMTP_PORT: {SMTP_PORT}")
        logger.error(f"SMTP_USERNAME: {SMTP_USERNAME}")
        logger.error(f"SMTP_TOKEN: {'Set' if SMTP_TOKEN else 'Not set'}")
        raise HTTPException(status_code=500, detail=error_msg)

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = "Reset Your Password"

        # Create the body of the message
        password_link = f"{FRONTEND_URL}/reset-password?token={token}"
        logger.info(f"Generated password reset link: {password_link}")
        
        body = f"""
        You have requested to reset your password.
        
        Please click the link below to reset your password:
        {password_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email and ensure your account is secure.
        """
        
        msg.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server and send email
        logger.info(f"Attempting to connect to SMTP server: {SMTP_HOST}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.set_debuglevel(1)  # Enable debug output
            logger.info("Starting TLS connection")
            server.starttls()
            
            logger.info("Attempting SMTP login")
            server.login(SMTP_USERNAME, SMTP_TOKEN)
            
            logger.info(f"Sending email to {email}")
            server.send_message(msg)
            logger.info("Email sent successfully")
            
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication failed: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error occurred: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
