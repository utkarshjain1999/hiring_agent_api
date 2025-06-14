from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class InterviewSlot(Base):
    __tablename__ = "interview_slots"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    interviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Refers to user table
    jd_id = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    reschedule_start_time = Column(DateTime, nullable=True)
    reschedule_end_time = Column(DateTime, nullable=True)
    is_rescheduled = Column(Boolean, default=False)
    reschedule_request_accept = Column(Boolean, default=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="slots")
    interviewer = relationship("User", back_populates="interview_slots")  # Assuming backref in User model
