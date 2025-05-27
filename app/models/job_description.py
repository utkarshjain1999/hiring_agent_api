from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base
from pydantic import BaseModel
from app.models.users import User  # Assuming interviewer info is in user table

# Association table
job_interviewers = Table(
    "job_interviewers",
    Base.metadata,
    Column("job_description_id", ForeignKey("job_descriptions.id"), primary_key=True),
    Column("interviewer_id", ForeignKey("users.id"), primary_key=True)
)

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

    interviewers = relationship("User", secondary=job_interviewers, back_populates="job_descriptions")

class JobDescriptionOut(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        orm_mode = True