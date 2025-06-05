from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer,ForeignKey
from app.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String, unique=True, index=True)
    status = Column(String, default="new")
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    jd_id = Column(Integer, ForeignKey("job_descriptions.id"))

    # ✅ Fix: Add this line
    interviews = relationship("Interview", back_populates="candidate")
    resume = relationship("Resume")
    job_description = relationship("JobDescription")

    def to_dict(self):
        return {"name": self.name, "phone": self.phone, "email": self.email, "status": self.status,"resume_id":self.resume_id, "jd_id":self.jd_id}

