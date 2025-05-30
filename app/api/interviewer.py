from fastapi import APIRouter, Depends, HTTPException, status
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
    try:
        return crud.create_interviewer(db, interviewer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the interviewer: {str(e)}"
        )

@router.get("/getAllInterviewers", response_model=list[schemas.InterviewerOut])
def get_all_interviewers(db: Session = Depends(get_db)):
    try:
        return crud.get_all_interviewers(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching interviewers: {str(e)}"
        )

@router.put("/updateInterviewer/{id}", response_model=schemas.InterviewerOut)
def update_interviewer(id: int, updates: schemas.InterviewerUpdate, db: Session = Depends(get_db)):
    try:
        updated = crud.update_interviewer(db, id, updates)
        if not updated:
            raise HTTPException(status_code=404, detail="Interviewer not found")
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the interviewer: {str(e)}"
        )

@router.delete("/deleteInterviewer/{id}")
def delete_interviewer(id: int, db: Session = Depends(get_db)):
    try:
        deleted = crud.delete_interviewer(db, id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Interviewer not found")
        return {"message": "Deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the interviewer: {str(e)}"
        )

@router.post("/createSlot", response_model=SlotOut)
def create_availability_slot(slot: CreateSlot, db: Session = Depends(get_db)):
    try:
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
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the slot: {str(e)}"
        )

