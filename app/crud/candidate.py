from sqlalchemy.orm import Session
from app.database import get_db
from app.models.candidate import Candidate
from app.models.resume import Resume
import pandas as pd
import json
from typing import Optional
import uuid
from fastapi import HTTPException

def add_candidate_to_db(name, phone, email,resume_id=None,jd_id=None):
    db = next(get_db())
    if not db.query(Candidate).filter_by(email=email,jd_id=jd_id).first():
        new_candidate = Candidate(
            name=name,
            phone=phone,
            email=email,
            status="new",
            resume_id=resume_id,
            jd_id=jd_id
        )
        db.add(new_candidate)
        db.commit()

def update_candidate_status(email, status):
    db = next(get_db())
    candidate = db.query(Candidate).filter_by(email=email).first()
    if candidate:
        candidate.status = status
        db.commit()
        return {"success": True}
    raise HTTPException(status_code=404, detail="Candidate not found")

def fetch_candidates(jd_id: int, search: Optional[str] = None):
    db = next(get_db())
    query = db.query(Candidate).filter(Candidate.jd_id == jd_id)

    if search:
        query = query.filter(
            Candidate.name.ilike(f"%{search}%") |
            Candidate.email.ilike(f"%{search}%")
        )

    candidates = query.all()

    grouped = {"new": [], "shortlisted": [], "hold": [], "rejected": []}
    for c in candidates:
        grouped.setdefault(c.status, []).append(c.to_dict())

    return grouped


def fetch_latest_resumes(db: Session,batch_id: Optional[str] = None):
    # db = next(get_db())

    if batch_id:
        try:
            batch_uuid = uuid.UUID(batch_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid batch_id format")
        resumes = db.query(Resume).filter(Resume.batch_id == batch_uuid).all()
    else:
        resumes = db.query(Resume).all()

    print(f"[DEBUG] Resumes fetched: {len(resumes)} for batch_id: {batch_id}")

    if not resumes:
        return pd.DataFrame()
    data = []
    for r in resumes:
        resume_dict = {
            "name": r.name,
            "email": r.email,
            "phone": r.phone,
            "college": r.college,
            "graduation_year": r.graduation_year,
            "skills": r.skills,
            "certification": r.certification,
            "experience": r.experience,
            "Intern_Experience": r.intern_experience,
        }
        data.append({
            "resume_id": r.id,
            "filename": r.source_file,
            "parsed_json": json.dumps(resume_dict)
        })
    return pd.DataFrame(data)


def get_candidate_by_id(db: Session, candidate_id: int):
    return db.query(Candidate).filter(Candidate.id == candidate_id).first()

