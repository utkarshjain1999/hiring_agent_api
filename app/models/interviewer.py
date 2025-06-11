from sqlalchemy import Column, Integer, DateTime,Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class InterviewerAvailability(Base):
    __tablename__ = "interviewer_availability"

    id = Column(Integer, primary_key=True, index=True)
    interviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    interviewer = relationship("User", back_populates="availability_slots")


