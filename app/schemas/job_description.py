from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RoundRequest(BaseModel):
    id: int
    title: str

class Interviewer(BaseModel):
    id: int
    name: str

class JobDescriptionSearchRequest(BaseModel):
    searchQuery: Optional[str] = None

class JDRequest(BaseModel):
    job_description: str
    job_title: str
    interviewer_ids: List[int]
    # round1: Optional[str] = None
    # round2: Optional[str] = None
    # round3: Optional[str] = None
    # round4: Optional[str] = None
    # round5: Optional[str] = None
    rounds: List[RoundRequest]

class JDResponse(BaseModel):
    # id: int
    # job_title: str
    # qualifications: Optional[str]
    # location: Optional[str]
    # experience_required: Optional[str]
    # required_skills: Optional[List[str]]
    # job_type: Optional[str]
    # company_name: Optional[str]
    # raw_jd_text: str
    # interviewer_ids: List[int]
    # created_at: Optional[datetime] = None
    # # round1: Optional[str] = None
    # # round2: Optional[str] = None
    # # round3: Optional[str] = None
    # # round4: Optional[str] = None
    # # round5: Optional[str] = None
    # rounds: List[RoundRequest]
    id: int
    title: str
    description: str
    created_at: datetime
    rounds: Optional[List[RoundRequest]] =  None
    interviewers: Optional[List[Interviewer]] =  None

# Add the missing JDUpdateRequest schema
class JDUpdateRequest(BaseModel):
    job_title: Optional[str] = None
    qualifications: Optional[str] = None
    location: Optional[str] = None
    experience_required: Optional[str] = None
    required_skills: Optional[List[str]] = None
    job_type: Optional[str] = None
    company_name: Optional[str] = None
    job_description: Optional[str] = None
    interviewer_ids: Optional[List[int]] = None
    round1: Optional[str] = None
    round2: Optional[str] = None
    round3: Optional[str] = None
    round4: Optional[str] = None
    round5: Optional[str] = None


    class Config:
        orm_mode = True
