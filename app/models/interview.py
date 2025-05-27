from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    interviewer_id = Column(Integer, ForeignKey("users.id"))
    scheduled_time = Column(DateTime)
    stage = Column(String)  # e.g., "Technical", "HR"
    status = Column(String, default="scheduled")  # scheduled, reschedule_requested, completed, etc.
    feedback = Column(Text, nullable=True)
    final_decision = Column(String, nullable=True)  # selected/rejected/hold

    candidate = relationship("Candidate", back_populates="interviews")
    interviewer = relationship("User")
