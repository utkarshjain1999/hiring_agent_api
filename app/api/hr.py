from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.schemas import hr as schemas
from app.crud import hr as crud
from sqlalchemy.orm import Session
from app.schemas.hr import *
from app.crud import hr
from app.crud.hr import get_all_invites
from app.database import get_db
from app.services.email_service import send_shortlist_email_with_slot_link_by_id
from app.models.candidate import Candidate
from app.models.interview import InterviewSlot  # Assuming this is your InterviewSlot model file
from app.schemas.interview_slot import InterviewSlotCreate, InterviewSlotResponse,VerifyTokenRequest, VerifyTokenResponse
from app.auth.jwt_handler import decode_email_token
from app.schemas.candidate import CandidateOut
from app.crud.candidate import fetch_shortlisted_candidates
from app.models.interviewer import InterviewerAvailability


router = APIRouter()

@router.post("/register-hr", response_model=schemas.HrOut)
def add_hr(hr: schemas.HrCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_hr(db, hr)
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

@router.get("/getAllShortlistedCandidates")
def get_shortlisted_candidates(
        jd_id: Optional[int] = Query(None),
        round_id: Optional[int] = Query(None),
        db: Session = Depends(get_db)
):
    candidates = fetch_shortlisted_candidates(db, jd_id, round_id)

    response = []
    for c in candidates:
        round_number = None
        round_data = None
        if round_id and c.jd and c.jd.rounds:
            for idx, r in enumerate(c.jd.rounds):
                if r["id"] == round_id:
                    round_number = idx + 1
                    round_data = r
                    break

        response.append({
            "id": c.id,
            "email": c.email,
            "name": c.name,
            "phone_number": c.phone_number,
            "shortlisted_date": c.shortlisted_date,
            "status": c.status,
            "jd_info": {
                "id": c.job_description.id if c.job_description else None,
                "title": c.job_description.job_title if c.job_description else None,
                "round": round_number  # Based on position in rounds list
            }
        })

    return response

# @router.post("/sendEmail")
# def send_email_api(req: EmailRequest, db: Session = Depends(get_db)):
#     return hr.send_stage_email(req, db)

@router.get("/getAllInterviewInvites")
def get_all_invites_route(
    jd_id: Optional[int] = None,
    round_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_all_invites(db, jd_id, round_id)

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
    # Step 1: Decode token to get candidate email
    try:
        email = decode_email_token(slot_data.token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Step 2: Get candidate
    candidate = db.query(Candidate).filter(Candidate.email == email).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Step 3: Get availability info
    availability = db.query(InterviewerAvailability).filter(
        InterviewerAvailability.id == slot_data.slot_id
    ).first()
    if not availability:
        raise HTTPException(status_code=404, detail="Selected availability not found")

    # Step 4: Check if candidate already has a booked slot
    slot = db.query(InterviewSlot).filter(
        InterviewSlot.candidate_id == candidate.id
    ).first()

    if slot:
        # Rescheduling
        slot.reschedule_start_time = availability.start_time
        slot.reschedule_end_time = availability.end_time
        slot.is_rescheduled = True
    else:
        # New booking
        slot = InterviewSlot(
            candidate_id=candidate.id,
            interviewer_id=availability.interviewer_id,
            jd_id=slot_data.jd_id,
            start_time=availability.start_time,
            end_time=availability.end_time,
            is_rescheduled=False,
            reschedule_request_accept=False
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
        reschedule_attempt = slot.is_rescheduled if slot and slot.is_rescheduled is not None else False
    )



