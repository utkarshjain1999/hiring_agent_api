from pyasn1.type.univ import Boolean
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InterviewSlotCreate(BaseModel):
    token: str  # Encoded candidate email
    jd_id: int
    slot_id: int

class InterviewSlotResponse(BaseModel):
    id: int
    candidate_id: int
    interviewer_id: int
    jd_id: int
    start_time: datetime
    end_time: datetime
    reschedule_start_time: Optional[datetime]
    reschedule_end_time: Optional[datetime]
    is_rescheduled: bool

    class Config:
        orm_mode = True


class VerifyTokenRequest(BaseModel):
    token: str

class VerifyTokenResponse(BaseModel):
    slot_status: str  # "new" or "reschedule"
    reschedule_attempt: bool


