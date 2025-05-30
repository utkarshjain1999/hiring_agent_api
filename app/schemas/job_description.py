from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JDRequest(BaseModel):
    jd_text: str
    interviewer_ids: List[int]
    round1: Optional[str] = None
    round2: Optional[str] = None
    round3: Optional[str] = None
    round4: Optional[str] = None
    round5: Optional[str] = None

class JDResponse(BaseModel):
    id: int
    job_title: Optional[str]
    qualifications: Optional[str]
    location: Optional[str]
    experience_required: Optional[str]
    required_skills: Optional[List[str]]
    job_type: Optional[str]
    company_name: Optional[str]
    raw_jd_text: str
    interviewer_ids: List[int]
    created_at: datetime
    round1: Optional[str]
    round2: Optional[str]
    round3: Optional[str]
    round4: Optional[str]
    round5: Optional[str]

    class Config:
        orm_mode = True

# Add the missing JDUpdateRequest schema
class JDUpdateRequest(BaseModel):
    job_title: Optional[str] = None
    qualifications: Optional[str] = None
    location: Optional[str] = None
    experience_required: Optional[str] = None
    required_skills: Optional[List[str]] = None
    job_type: Optional[str] = None
    company_name: Optional[str] = None
    raw_jd_text: Optional[str] = None
    interviewer_ids: Optional[List[int]] = None
    round1: Optional[str] = None
    round2: Optional[str] = None
    round3: Optional[str] = None
    round4: Optional[str] = None
    round5: Optional[str] = None
