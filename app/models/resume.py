from sqlalchemy import Column, Integer, String, ARRAY, JSON
from app.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    college = Column(String)
    graduation_year = Column(Integer)
    skills = Column(ARRAY(String))
    certification = Column(ARRAY(String))
    experience = Column(Integer)
    intern_experience = Column(JSON)
    source_file = Column(String)
