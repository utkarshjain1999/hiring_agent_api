from sqlalchemy import Column, Integer, String, event, Boolean, DateTime
from app.database import Base
from sqlalchemy.orm import relationship
from app.models.associations import job_interviewers
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Made nullable since we'll set it later
    role = Column(String)
    availability_slots = relationship("InterviewerAvailability", back_populates="interviewer")
    
    # Password related fields
    password_setup_token_used = Column(Boolean, default=False)  # Track if setup token has been used
    password_last_changed = Column(DateTime, nullable=True)  # Track when password was last changed
    password_setup_required = Column(Boolean, default=True)  # Track if initial password setup is required

    # inside User model
    job_descriptions = relationship("JobDescription", secondary=job_interviewers, back_populates="interviewers")

def send_password_setup_email_for_user(user):
    """Helper function to send password setup email"""
    logger.info(f"Attempting to send password setup email for user: {user.email}")
    if user.password_setup_required:
        try:
            # Import here to avoid circular imports
            from app.services.email_service import generate_password_setup_token, send_password_setup_email
            # Generate token and send email
            logger.info("Generating password setup token")
            token = generate_password_setup_token(user.email)
            logger.info("Sending password setup email")
            send_password_setup_email(user.email, token)
            logger.info("Password setup email sent successfully")
        except Exception as e:
            # Log the error but don't raise it to prevent transaction rollback
            logger.error(f"Failed to send password setup email to {user.email}: {str(e)}")
            print(f"Failed to send password setup email to {user.email}: {str(e)}")
    else:
        logger.info(f"User {user.email} already has a password set, skipping email")

@event.listens_for(User, 'after_insert')
def send_password_setup_email_after_insert(mapper, connection, target):
    """Event listener that triggers after a new user is inserted"""
    logger.info(f"User created event triggered for: {target.email}")
    send_password_setup_email_for_user(target)
