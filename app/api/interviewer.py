from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import interviewer as schemas
from app.crud import interviewer as crud
from app.database import get_db
from app.models.interviewer import InterviewerAvailability
from app.schemas.interviewer import CreateSlot, SlotOut,BulkSlotRequest
from datetime import datetime
from typing import List
from app.schemas.interviewer import InterviewerIdRequest,AvailabilityResponse, SlotInfo, AvailabilityByDate
from collections import defaultdict

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

@router.post("/createSlot", response_model=List[SlotOut])
def create_availability_slot(payload: BulkSlotRequest, db: Session = Depends(get_db)):
    created_slots = []
    try:
        for slot in payload.availability:
            start_time = datetime.strptime(slot.start, "%H:%M").time()
            end_time = datetime.strptime(slot.end, "%H:%M").time()

            start_datetime = datetime.combine(slot.date.date(), start_time)
            end_datetime = datetime.combine(slot.date.date(), end_time)

            db_slot = InterviewerAvailability(
                interviewer_id=payload.userId,
                date=slot.date.date(),
                start_time=start_datetime,
                end_time=end_datetime
            )
            db.add(db_slot)
            db.commit()
            db.refresh(db_slot)
            created_slots.append(db_slot)

        return created_slots

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the slots: {str(e)}"
        )

@router.post("/getAllSlots", response_model=AvailabilityResponse)
def get_available_slots(
    req: InterviewerIdRequest,
    db: Session = Depends(get_db)
):
    try:
        current_time = datetime.now()
        # Fetch slots for this interviewer
        slots = db.query(InterviewerAvailability).filter(
            InterviewerAvailability.interviewer_id == req.interviewerId,
            InterviewerAvailability.start_time > current_time
        ).order_by(InterviewerAvailability.date, InterviewerAvailability.start_time).all()

        # Group slots by date
        grouped = defaultdict(list)
        for slot in slots:
            grouped[slot.date].append(slot)

        availability = []
        for slot_date, slots_on_date in grouped.items():
            slot_infos = []
            for s in slots_on_date:
                slot_infos.append(
                    SlotInfo(
                        id=s.id,
                        start=s.start_time.strftime("%H:%M"),
                        end=s.end_time.strftime("%H:%M"),
                        timezone="Asia/Kolkata",
                        interviewer_id=s.interviewer_id,
                        # jdId=getattr(s, 'jd_id', None)  # if jd_id exists in your model
                    )
                )
            availability.append(
                AvailabilityByDate(
                    date=slot_date,
                    slots=slot_infos
                )
            )

        return AvailabilityResponse(availability=availability)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
