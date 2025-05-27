from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.resume_matcher import ResumeMatcher
from app.schemas.candidate import MatchingRequest
from app.crud import resume as resume_crud
from typing import List, Dict

router = APIRouter()
matcher = ResumeMatcher()

@router.post("/match")
async def match_resumes(request: MatchingRequest, db: Session = Depends(get_db)) -> List[Dict]:
    # Get all resumes from database
    resumes = resume_crud.get_all_resumes(db)
    
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found in database")
    
    # Convert SQLAlchemy models to dictionaries
    resume_dicts = [
        {
            'id': resume.id,
            'candidate_id': resume.candidate_id,
            'content': resume.content
        }
        for resume in resumes
    ]
    
    # Match resumes against job description
    matches = matcher.match_resumes(
        jd_text=request.jd_text,
        resumes=resume_dicts,
        threshold=request.threshold,
        top_n=request.top_n
    )
    
    return matches 