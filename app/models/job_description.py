from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from pydantic import BaseModel
from datetime import datetime
from app.models.associations import job_interviewers

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String)
    qualifications = Column(String)
    location = Column(String)
    experience_required = Column(String)
    required_skills = Column(Text)
    job_type = Column(String)
    company_name = Column(String)
    raw_jd_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    round1 = Column(Text)
    round2 = Column(Text)
    round3 = Column(Text)
    round4 = Column(Text)
    round5 = Column(Text)

    interviewers = relationship("User", secondary=job_interviewers, back_populates="job_descriptions")

class JobDescriptionOut(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime

    class Config:
        orm_mode = True