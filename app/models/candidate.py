from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer,ForeignKey, DateTime
from app.database import Base
from datetime import datetime

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone_number = Column(String)
    email = Column(String, unique=True, index=True)
    status = Column(String, default="new")
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    jd_id = Column(Integer, ForeignKey("job_descriptions.id"))
    shortlisted_date = Column(DateTime, nullable=True)

    # ✅ Fix: Add this line
    interviews = relationship("InterviewSlot", back_populates="candidate")
    resume = relationship("Resume")
    job_description = relationship("JobDescription", back_populates="candidates")
    slots = relationship("InterviewSlot", back_populates="candidate")

    def to_dict(self):
        return {"name": self.name, "phone_number": self.phone_number, "email": self.email, "status": self.status,"resume_id":self.resume_id, "jd_id":self.jd_id}

