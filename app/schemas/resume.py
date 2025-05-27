from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ResumeBase(BaseModel):
    candidate_id: int
    file_path: str
    content: str

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(BaseModel):
    content: Optional[str] = None
    file_path: Optional[str] = None

class ResumeInDB(ResumeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 