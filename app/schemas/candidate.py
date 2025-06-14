from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import DateTime
from datetime import datetime

class CandidateQuery(BaseModel):
    jdId: int
    searchQuery: Optional[str] = None

class InternExperience(BaseModel):
    duration_months: Optional[int]
    roles: Optional[List[str]]
    durations: Optional[List[str]]
    companies: Optional[List[str]]
    locations: Optional[List[str]]

class ResumeCreate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    college: Optional[str]
    graduation_year: Optional[int]
    skills: Optional[List[str]]
    certification: Optional[List[str]]
    experience: Optional[int]
    intern_experience: Optional[InternExperience]
    source_file: Optional[str]

class JDInfo(BaseModel):
    id: Optional[int]
    title: Optional[str]
    round: Optional[int]

    class Config:
        orm_mode = True

class CandidateOut(BaseModel):
    id: Optional[int]
    email: Optional[str]
    name: Optional[str]
    phone_number: Optional[str]
    jd: Optional[JDInfo]
    shortlisted_date: Optional[datetime]
    status: Optional[str]

    class Config:
        orm_mode = True
