from sqlalchemy.orm import Session
from app.models.job_description import JobDescription
from app.models.users import User
from app.services.jd_parser import extract_jd_data

def extract_and_store_jd(jd_text: str, interviewer_ids: list[int], db: Session):
    result = extract_jd_data(jd_text)
    if result:
        jd = JobDescription(
            job_title=result.get("job_title"),
            qualifications=result.get("qualifications"),
            location=result.get("location"),
            experience_required=result.get("experience_required"),
            required_skills=", ".join(result.get("required_skills") or []),
            job_type=result.get("job_type"),
            company_name=result.get("company_name"),
            raw_jd_text=jd_text,
        )

        interviewers = db.query(User).filter(User.id.in_(interviewer_ids)).all()
        jd.interviewers.extend(interviewers)

        db.add(jd)
        db.commit()
        db.refresh(jd)
        return jd
    return None

def get_all_job_descriptions():
    from app.database import SessionLocal  # assuming this gives a session
    session = SessionLocal()
    try:
        return session.query(JobDescription).all()
    finally:
        session.close()

