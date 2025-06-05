from pydantic import BaseModel
from typing import List, Optional

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
