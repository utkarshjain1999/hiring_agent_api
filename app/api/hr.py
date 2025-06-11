from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.hr import *
from app.crud import hr
from app.database import get_db
from app.services.email_service import send_shortlist_email_with_slot_link_by_id
from app.models.candidate import Candidate
from app.models.interview import InterviewSlot  # Assuming this is your InterviewSlot model file
from app.schemas.interview_slot import InterviewSlotCreate, InterviewSlotResponse,VerifyTokenRequest, VerifyTokenResponse
from app.auth.jwt_handler import decode_email_token


router = APIRouter()

@router.get("/getAllShortlistedCandidates")
def get_shortlisted(db: Session = Depends(get_db)):
    return hr.fetch_shortlisted_candidates(db)

# @router.post("/sendEmail")
# def send_email_api(req: EmailRequest, db: Session = Depends(get_db)):
#     return hr.send_stage_email(req, db)

@router.get("/getAllInterviewInvites")
def get_invites(db: Session = Depends(get_db)):
    return hr.get_all_invites(db)

@router.get("/getAllRescheduleRequests")
def get_reschedules(db: Session = Depends(get_db)):
    return hr.get_all_reschedule_requests(db)

@router.post("/approveRescheduleReq")
def approve_reschedule(req: RescheduleAction, db: Session = Depends(get_db)):
    return hr.approve_reschedule(db, req)

@router.post("/rejectRescheduleReq")
def reject_reschedule(req: RescheduleAction, db: Session = Depends(get_db)):
    return hr.reject_reschedule(db, req)

@router.post("/candidateFeedback")
def submit_feedback(req: CandidateFeedback, db: Session = Depends(get_db)):
    return hr.submit_feedback(db, req)

@router.post("/actionOnFeedback")
def final_decision(req: FinalDecision, db: Session = Depends(get_db)):
    return hr.finalize_decision(db, req)

@router.post("/sendmail")
def send_emails(request: SendMailRequest, db: Session = Depends(get_db)):

    if request.candidate_ids:
        for candidate_id in request.candidate_ids:
            send_shortlist_email_with_slot_link_by_id(candidate_id, db)

    # Add logic for interview_ids if needed

    return {"message": "Emails sent successfully."}

@router.post("/book-slot", response_model=InterviewSlotResponse)
def book_interview_slot(slot_data: InterviewSlotCreate, db: Session = Depends(get_db)):
    # Step 1: Lookup candidate
    candidate = db.query(Candidate).filter(Candidate.email == slot_data.email).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Optional: Check if slot already booked
    conflict = db.query(InterviewSlot).filter(
        InterviewSlot.candidate_id == candidate.id,
        InterviewSlot.start_time == slot_data.start_time
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="Slot already booked")

    # Step 2: Create slot
    slot = InterviewSlot(
        candidate_id=candidate.id,
        interviewer_id=slot_data.interviewer_id,  # User table ID
        jd_id=slot_data.jd_id,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)

    return slot


@router.post("/verify-rescheduling", response_model=VerifyTokenResponse)
def verify_rescheduling(data: VerifyTokenRequest, db: Session = Depends(get_db)):
    email = decode_email_token(data.token)

    candidate = db.query(Candidate).filter(Candidate.email == email).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    slot = db.query(InterviewSlot).filter(InterviewSlot.candidate_id == candidate.id).first()

    return VerifyTokenResponse(
        slot_status="reschedule" if slot else "new",
        candidate_id=candidate.id
    )



