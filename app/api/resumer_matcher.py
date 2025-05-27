from fastapi import APIRouter, Query, HTTPException
from app.schemas.resume_candidate import CandidateData, MatchingRequest
from app.services.screening import match_resumes_service, shortlist_candidate, hold_candidate, reject_candidate, export_candidates_to_excel, get_candidates_by_status
from app.crud.job_description import get_all_job_descriptions

router = APIRouter()

@router.get("/getAllJobDescriptions")
async def get_all_jds():
    """Fetch all job descriptions for dropdown or filtering."""
    try:
        jds = get_all_job_descriptions()
        return {"job_descriptions": jds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job descriptions: {str(e)}")

@router.get("/candidates")
def get_candidates(status: str = Query(...), search: str = Query(None)):
    return get_candidates_by_status(status, search)

@router.post("/shortlist")
def shortlist(data: CandidateData):
    return shortlist_candidate(data)

@router.post("/hold")
def hold(data: CandidateData):
    return hold_candidate(data)

@router.post("/reject")
def reject(data: CandidateData):
    return reject_candidate(data)

@router.post("/match_resumes")
def match_resumes(request: MatchingRequest):
    return match_resumes_service(request)

@router.get("/exportToExcel")
def export_excel():
    return export_candidates_to_excel()
