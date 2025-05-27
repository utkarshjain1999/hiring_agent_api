from pydantic import BaseModel
from typing import List, Optional

class JDRequest(BaseModel):
    jd_text: str
    interviewer_ids: List[int]

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
