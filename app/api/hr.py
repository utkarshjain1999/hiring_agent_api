from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.hr import *
from app.crud import hr
from app.core.dependencies import get_db

router = APIRouter()

@router.get("/getAllShortlistedCandidates")
def get_shortlisted(db: Session = Depends(get_db)):
    return hr.fetch_shortlisted_candidates(db)

@router.post("/sendEmail")
def send_email_api(req: EmailRequest, db: Session = Depends(get_db)):
    return hr.send_stage_email(req, db)

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
