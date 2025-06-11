from sqlalchemy import Column, Integer, ForeignKey, DateTime
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

    # Relationships
    candidate = relationship("Candidate", back_populates="slots")
    interviewer = relationship("User", back_populates="interview_slots")  # Assuming backref in User model
