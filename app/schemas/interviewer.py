from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, time, datetime

PHONE_PATTERN = r'^\+?1?\d{9,15}$'

class InterviewerCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str = Field(..., pattern=PHONE_PATTERN)

class InterviewerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, pattern=PHONE_PATTERN)

class InterviewerOut(BaseModel):
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

class CreateSlot(BaseModel):
    interviewer_id: int
    date: date  # YYYY-MM-DD
    start_time: time  # HH:MM:SS
    end_time: time  # HH:MM:SS

class SlotOut(BaseModel):
    id: int
    interviewer_id: int
    date: date
    start_time: datetime
    end_time: datetime

    class Config:
        orm_mode = True


class AvailabilityItem(BaseModel):
    date: datetime  # Accepts ISO format with timestamp
    start: str      # "09:00"
    end: str        # "09:30"
    timezone: str   # Optional for now

class BulkSlotRequest(BaseModel):
    userId: int
    availability: List[AvailabilityItem]

class SlotInfo(BaseModel):
    id: int
    start: str
    end: str
    timezone: str = "Asia/Kolkata"  # default timezone as per your example
    jdId: Optional[int] = None
    interviewer_id: Optional[int] = None

class AvailabilityByDate(BaseModel):
    date: date
    slots: List[SlotInfo]

class AvailabilityResponse(BaseModel):
    availability: List[AvailabilityByDate]

class InterviewerIdRequest(BaseModel):
    interviewerId: int
