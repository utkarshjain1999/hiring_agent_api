from sqlalchemy.orm import Session
from app.models.job_description import JobDescription
from app.models.users import User
from app.services.jd_parser import extract_jd_data
from app.database import SessionLocal
from typing import List
from app.schemas.job_description import RoundRequest


def extract_and_store_jd(job_description: str,job_title: str, interviewer_ids: list[int], db: Session, rounds: List[RoundRequest]):
    print(f"Type of db received: {type(db)}")
    result = extract_jd_data(job_description)
    if result:
        round_titles = {f"round{r.id}": r.title for r in rounds if 1 <= r.id <= 5}
        jd = JobDescription(
            job_title=job_title,
            qualifications=result.get("qualifications"),
            location=result.get("location"),
            experience_required=result.get("experience_required"),
            required_skills=", ".join(result.get("required_skills") or []),
            job_type=result.get("job_type"),
            company_name=result.get("company_name"),
            raw_jd_text=job_description,
            # round1=round1,
            # round2=round2,
            # round3=round3,
            # round4=round4,
            # round5=round5
            round1=round_titles.get("round1"),
            round2=round_titles.get("round2"),
            round3=round_titles.get("round3"),
            round4=round_titles.get("round4"),
            round5=round_titles.get("round5")
        )

        interviewers = db.query(User).filter(User.id.in_(interviewer_ids)).all()
        jd.interviewers.extend(interviewers)

        db.add(jd)
        db.commit()
        db.refresh(jd)
        return jd
    return None

def get_all_job_descriptions(db: Session = None):
    # from app.database import SessionLocal  # assuming this gives a session
    # session = SessionLocal()
    # try:
    #     return session.query(JobDescription).all()
    # finally:
    #     session.close()
    """
        Optional `db` parameter allows reuse inside FastAPI routes or as standalone.
        """
    local_session = False

    if db is None:
        db = SessionLocal()
        local_session = True

    try:
        return db.query(JobDescription).all()
    finally:
        if local_session:
            db.close()


