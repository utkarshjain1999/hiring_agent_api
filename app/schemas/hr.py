from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from typing import List
from datetime import date, time, datetime

PHONE_PATTERN = r'^\+?1?\d{9,15}$'

class HrCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str = Field(..., pattern=PHONE_PATTERN)

class HrUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, pattern=PHONE_PATTERN)

class HrOut(BaseModel):
    id: int
    name: str
    email: str
    phone_number: str
    role: str

    class Config:
        orm_mode = True
        # Allow extra fields from the model
        extra = "allow"
        # Convert None values to empty strings for string fields
        json_encoders = {
            str: lambda v: v if v is not None else ""
        }
class SendMailRequest(BaseModel):
    candidate_ids: Optional[List[int]] = None
    interview_ids: Optional[List[int]] = None

class RescheduleAction(BaseModel):
    interview_slot_id: int

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
