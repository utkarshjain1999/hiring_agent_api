from fastapi import APIRouter, Query, HTTPException
from app.schemas.resume_candidate import CandidateData, MatchingRequest
from app.services.screening import match_resumes_service, update_candidate_status_by_resume, export_candidates_to_excel,fetch_candidates
from app.crud.job_description import get_all_job_descriptions
from app.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from app.schemas.candidate import CandidateQuery

router = APIRouter()

@router.get("/getAllJobDescriptions")
async def get_all_jds():
    """Fetch all job descriptions for dropdown or filtering."""
    try:
        jds = get_all_job_descriptions()
        return {"job_descriptions": jds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job descriptions: {str(e)}")

@router.post("/candidates")
def get_candidates(query: CandidateQuery):
    return fetch_candidates(jd_id=query.jdId, search=query.searchQuery)


@router.post("/job-descriptions/{jd_id}/{status}/{resume_id}")
def update_candidate_status_endpoint(jd_id: int, status: str, resume_id: int):
    valid_statuses = {"shortlisted", "hold", "rejected"}
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status value")

    return update_candidate_status_by_resume(resume_id=resume_id, status=status)

@router.post("/match_resumes")
def match_resumes(request: MatchingRequest, db: Session = Depends(get_db)):
    return match_resumes_service(request, db)

@router.get("/exportToExcel/{jd_id}")
def export_excel(jd_id: str):
    return export_candidates_to_excel(jd_id)

