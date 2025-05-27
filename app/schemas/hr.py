from pydantic import BaseModel, EmailStr
from typing import Optional

class EmailRequest(BaseModel):
    candidate_id: int
    stage: str

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
