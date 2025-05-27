from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

class InterviewerCreate(BaseModel):
    username: str
    password: str  # Raw password input

class InterviewerUpdate(BaseModel):
    username: Optional[str]
    password: Optional[str]

class InterviewerOut(BaseModel):
    id: int
    username: str
    role: str

class CreateSlot(BaseModel):
    interviewer_id: int
    date: date  # YYYY-MM-DD
    start_time: time  # HH:MM:SS
    end_time: time  # HH:MM:SS

class SlotOut(BaseModel):
    id: int
    interviewer_id: int
    start_time: datetime
    end_time: datetime

    class Config:
        orm_mode = True
