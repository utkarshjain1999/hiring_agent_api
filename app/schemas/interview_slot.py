from pydantic import BaseModel
from datetime import datetime

class InterviewSlotCreate(BaseModel):
    email: str
    interviewer_id: int  # User ID
    jd_id: int
    start_time: datetime
    end_time: datetime

class InterviewSlotResponse(BaseModel):
    id: int
    candidate_id: int
    interviewer_id: int
    jd_id: int
    start_time: datetime
    end_time: datetime

    class Config:
        orm_mode = True


class VerifyTokenRequest(BaseModel):
    token: str

class VerifyTokenResponse(BaseModel):
    slot_status: str  # "new" or "reschedule"
    candidate_id: int


