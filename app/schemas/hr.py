from pydantic import BaseModel, EmailStr
from typing import Optional
from typing import List


class SendMailRequest(BaseModel):
    candidate_ids: Optional[List[int]] = None
    interview_ids: Optional[List[int]] = None

class RescheduleAction(BaseModel):
    interview_id: int

class HRRegistration(BaseModel):
    name: str
    email: EmailStr
    password: str

class CandidateFeedback(BaseModel):
    interview_id: int
    feedback: str

class FinalDecision(BaseModel):
    interview_id: int
    decision: str  # selected/rejected/hold
