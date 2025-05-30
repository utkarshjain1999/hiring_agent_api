from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import re

PHONE_PATTERN = r'^\+?1?\d{9,15}$'

class CompanyCreate(BaseModel):
    full_name: str
    domain: str
    company_name: str
    phone_number: str = Field(..., pattern=PHONE_PATTERN)
    email: EmailStr
    designation: str

class CompanyOut(BaseModel):
    comp_id: int
    full_name: str
    domain: str
    company_name: str
    phone_number: str
    email: EmailStr
    designation: str

    class Config:
        orm_mode = True
