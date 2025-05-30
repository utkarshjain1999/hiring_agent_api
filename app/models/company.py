from sqlalchemy import Column, Integer, String
from app.database import Base

class Company(Base):
    __tablename__ = "companies"

    comp_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    domain = Column(String, nullable=False, unique=True, index=True)
    company_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    designation = Column(String, nullable=False)
