from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import interviewer as schemas
from app.crud import interviewer as crud
from app.database import get_db
from app.models.interviewer import InterviewerAvailability
from app.schemas.interviewer import CreateSlot, SlotOut
from datetime import datetime

router = APIRouter()

@router.post("/addInterviewer", response_model=schemas.InterviewerOut)
def add_interviewer(interviewer: schemas.InterviewerCreate, db: Session = Depends(get_db)):
    return crud.create_interviewer(db, interviewer)

@router.get("/getAllInterviewers", response_model=list[schemas.InterviewerOut])
def get_all_interviewers(db: Session = Depends(get_db)):
    return crud.get_all_interviewers(db)

@router.put("/updateInterviewer/{id}", response_model=schemas.InterviewerOut)
def update_interviewer(id: int, updates: schemas.InterviewerUpdate, db: Session = Depends(get_db)):
    updated = crud.update_interviewer(db, id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Interviewer not found")
    return updated

@router.delete("/deleteInterviewer/{id}")
def delete_interviewer(id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_interviewer(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Interviewer not found")
    return {"message": "Deleted successfully"}

@router.post("/createSlot", response_model=SlotOut)
def create_availability_slot(slot: CreateSlot, db: Session = Depends(get_db)):
    # Create datetime objects by combining date and time
    start_datetime = datetime.combine(slot.date, slot.start_time)
    end_datetime = datetime.combine(slot.date, slot.end_time)
    
    db_slot = InterviewerAvailability(
        interviewer_id=slot.interviewer_id,
        date=slot.date,
        start_time=start_datetime,
        end_time=end_datetime
    )
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

