from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer
from app.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String, unique=True, index=True)
    status = Column(String, default="new")

    # ✅ Fix: Add this line
    interviews = relationship("Interview", back_populates="candidate")

    def to_dict(self):
        return {"name": self.name, "phone": self.phone, "email": self.email, "status": self.status}

