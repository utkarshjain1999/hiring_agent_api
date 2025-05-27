from pydantic import BaseModel, EmailStr
from typing import Optional

class CandidateData(BaseModel):
    name: str
    phone: Optional[str]
    email: EmailStr

class MatchingRequest(BaseModel):
    jd_text: str
    threshold: float = 0.7
    top_n: int = 10
