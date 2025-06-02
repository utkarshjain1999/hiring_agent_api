from pydantic import BaseModel, EmailStr
from typing import Optional

class CandidateData(BaseModel):
    name: str
    phone: Optional[str]
    email: EmailStr

class MatchingRequest(BaseModel):
    jd_id: int
    threshold: float = 0.7
    top_n: int = 5
    batch_id: Optional[str] = None

class MatchingRequestByBatch(BaseModel):
    batch_id: str
    jd_id: str
    threshold: float = 0.7
    top_n: int = 5
