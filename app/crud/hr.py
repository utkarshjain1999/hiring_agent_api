from sqlalchemy.orm import Session
from app.models.interview import InterviewSlot
from app.models.users import User
from app.models.candidate import Candidate
from app.schemas.hr import *
from app.core.utils import send_email
from sqlalchemy.orm import joinedload
from app.services.email_service import send_generic_email
from app.crud.candidate import get_candidate_by_id

def fetch_shortlisted_candidates(db: Session):
    return db.query(Candidate).filter(Candidate.status == "shortlisted").all()

# def send_stage_email(req: EmailRequest, db: Session):
#     candidate = db.query(Candidate).filter(Candidate.id == req.candidate_id).first()
#     if not candidate:
#         return {"error": "Candidate not found"}
#     subject = f"Interview Update - {req.stage} Stage"
#     body = f"Dear {candidate.name},\n\nYou are invited for the {req.stage} round.\n\nRegards,\nHR Team"
#     send_email(to=candidate.email, subject=subject, body=body)
#     return {"message": "Email sent successfully"}

def create_hr(db: Session, hr: HrCreate):
    # Check if email or phone number already exists
    existing_user = db.query(User).filter(
        (User.email == hr.email) |
        (User.phone_number == hr.phone_number)
    ).first()

    if existing_user:
        raise ValueError("Email or phone number already registered")

    db_user = User(
        name=hr.name,
        email=hr.email,
        phone_number=hr.phone_number,
        role="hr"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_invites(db: Session, jd_id: Optional[int] = None, round_id: Optional[int] = None):
    query = db.query(InterviewSlot)\
        .options(
            joinedload(InterviewSlot.candidate).joinedload(Candidate.job_description),
            joinedload(InterviewSlot.interviewer)
        )
        # .filter(InterviewSlot.jd_id == "scheduled")

    if jd_id:
        query = query.join(InterviewSlot.candidate).filter(Candidate.jd_id == jd_id)
    if round_id:
        query = query.filter(Candidate.round_id == round_id)

    slots = query.all()

    result = []
    for slot in slots:
        candidate = slot.candidate
        interviewer = slot.interviewer
        jd = candidate.job_description if candidate else None

        result.append({

            "candidate": {
                "id": candidate.id,
                "email": candidate.email,
                "name": candidate.name,
                "phone_number": candidate.phone_number,
                "shortlisted_date": candidate.shortlisted_date,
                "status": candidate.status,
            },
            "interviewer": {
                "id": interviewer.id,
                "email": interviewer.email,
                "name": interviewer.name
            } if interviewer else None,
            "jd_info": {
                "id": jd.id,
                "title": jd.job_title
            } if jd else None,
            "interview_slot": {
                "id": slot.id,
                "start": slot.start_time.strftime("%H:%M"),
                "end": slot.end_time.strftime("%H:%M"),
                "date": slot.start_time.date().isoformat()
            },
            "status": "invited"
        })

    return result


def get_all_reschedule_requests(db: Session):
    # Fetch slots where reschedule flag is True, with candidate and JD info eagerly loaded
    slots = db.query(InterviewSlot)\
        .filter(InterviewSlot.is_rescheduled == "true")\
        .options(
            joinedload(InterviewSlot.candidate).joinedload(Candidate.job_description) # assuming this relationship exists
        )\
        .all()

    response = []
    for slot in slots:
        if not slot.candidate or not slot.jd_id:
            continue

        response.append({
            "candidate": {
                "id": slot.candidate.id,
                "email": slot.candidate.email,
                "name": slot.candidate.name,
                "phone_number": slot.candidate.phone_number,
                "shortlisted_date": slot.candidate.shortlisted_date,
                "status": slot.candidate.status
            },
            "jd_info": {
                "id": slot.jd_id,
                "title": slot.candidate.job_description.job_title if slot.candidate.job_description else None
            },
            "old_slot": {
                "start_time": slot.start_time.isoformat(),
                "end_time": slot.end_time.isoformat()
            },
            "rescheduled_slot": {
                "start_time": slot.reschedule_start_time.isoformat() if slot.reschedule_start_time else None,
                "end_time": slot.reschedule_end_time.isoformat() if slot.reschedule_end_time else None
            }
        })

    return response

def approve_reschedule(db: Session, req: RescheduleAction):
    # Step 1: Get the interview slot
    interview = db.query(InterviewSlot).get(req.interview_slot_id)
    if not interview:
        return {"error": "Interview not found"}

    # Step 2: Update reschedule_request_accept
    interview.reschedule_request_accept = True

    # Step 3: Update start and end time to new rescheduled time
    interview.start_time = interview.reschedule_start_time
    interview.end_time = interview.reschedule_end_time

    db.commit()

    # Step 4: Get candidate_id from interview
    candidate_id = interview.candidate_id

    # Step 5: Fetch candidate details from candidate_id (using your existing function)
    candidate = get_candidate_by_id(db, candidate_id)  # <-- You said this function exists

    # Step 6: Send email if candidate found
    if candidate:
        subject = "Interview Reschedule Approved"
        body = f"""
        Dear {candidate.name},

        Your interview reschedule request has been approved.

        📅 New Date: {interview.start_time.date().isoformat()}
        🕒 Time: {interview.start_time.strftime('%H:%M')} - {interview.end_time.strftime('%H:%M')}

        Please make sure to be available on time.

        Regards,  
        HR Team
        """
        send_generic_email(to_email=candidate.email, subject=subject, body=body)

    return {"message": "Reschedule approved and email sent"}


def reject_reschedule(db: Session, req: RescheduleAction):
    interview = db.query(InterviewSlot).get(req.interview_id)
    if interview:
        interview.status = "scheduled"
        db.commit()
        return {"message": "Reschedule rejected"}
    return {"error": "Interview not found"}

def submit_feedback(db: Session, req: CandidateFeedback):
    interview = db.query(InterviewSlot).get(req.interview_id)
    if interview:
        interview.feedback = req.feedback
        db.commit()
        return {"message": "Feedback submitted"}
    return {"error": "Interview not found"}

def finalize_decision(db: Session, req: FinalDecision):
    interview = db.query(InterviewSlot).get(req.interview_id)
    if interview:
        interview.final_decision = req.decision
        db.commit()
        return {"message": "Final decision recorded"}
    return {"error": "Interview not found"}
