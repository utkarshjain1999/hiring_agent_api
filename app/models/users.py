from sqlalchemy import Column, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)
    availability_slots = relationship("InterviewerAvailability", back_populates="interviewer")

    # inside User model
    job_descriptions = relationship("JobDescription", secondary="job_interviewers", back_populates="interviewers")
