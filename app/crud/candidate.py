from sqlalchemy.orm import Session
from app.database import get_db
from app.models.candidate import Candidate
from app.models.resume import Resume
import pandas as pd
import json
from typing import Optional
import uuid
from fastapi import HTTPException

def add_candidate_to_db(name, phone, email):
    db = next(get_db())
    if not db.query(Candidate).filter_by(email=email).first():
        new_candidate = Candidate(name=name, phone=phone, email=email, status="new")
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

def fetch_candidates(status, search=None):
    db = next(get_db())
    query = db.query(Candidate)
    if status != "all":
        query = query.filter_by(status=status)
    if search:
        query = query.filter(Candidate.name.ilike(f"%{search}%") | Candidate.email.ilike(f"%{search}%"))
    results = query.all()
    return pd.DataFrame([c.to_dict() for c in results])

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
            "filename": r.source_file,
            "parsed_json": json.dumps(resume_dict)
        })
    return pd.DataFrame(data)
