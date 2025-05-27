from sqlalchemy.orm import Session
from app.models import Interview, Candidate, User
from app.schemas.hr import *
from app.core.utils import send_email

def fetch_shortlisted_candidates(db: Session):
    return db.query(Candidate).filter(Candidate.status == "shortlisted").all()

def send_stage_email(req: EmailRequest, db: Session):
    candidate = db.query(Candidate).filter(Candidate.id == req.candidate_id).first()
    if not candidate:
        return {"error": "Candidate not found"}
    subject = f"Interview Update - {req.stage} Stage"
    body = f"Dear {candidate.name},\n\nYou are invited for the {req.stage} round.\n\nRegards,\nHR Team"
    send_email(to=candidate.email, subject=subject, body=body)
    return {"message": "Email sent successfully"}

def get_all_invites(db: Session):
    return db.query(Interview).filter(Interview.status == "scheduled").all()

def get_all_reschedule_requests(db: Session):
    return db.query(Interview).filter(Interview.status == "reschedule_requested").all()

def approve_reschedule(db: Session, req: RescheduleAction):
    interview = db.query(Interview).get(req.interview_id)
    if interview:
        interview.status = "rescheduled"
        db.commit()
        return {"message": "Reschedule approved"}
    return {"error": "Interview not found"}

def reject_reschedule(db: Session, req: RescheduleAction):
    interview = db.query(Interview).get(req.interview_id)
    if interview:
        interview.status = "scheduled"
        db.commit()
        return {"message": "Reschedule rejected"}
    return {"error": "Interview not found"}

def submit_feedback(db: Session, req: CandidateFeedback):
    interview = db.query(Interview).get(req.interview_id)
    if interview:
        interview.feedback = req.feedback
        db.commit()
        return {"message": "Feedback submitted"}
    return {"error": "Interview not found"}

def finalize_decision(db: Session, req: FinalDecision):
    interview = db.query(Interview).get(req.interview_id)
    if interview:
        interview.final_decision = req.decision
        db.commit()
        return {"message": "Final decision recorded"}
    return {"error": "Interview not found"}
