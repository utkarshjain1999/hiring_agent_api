from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.job_description import JDRequest, JDResponse, JDUpdateRequest
from app.models.job_description import JobDescription
from app.models.users import User
from app.database import get_db
from app.crud.job_description import extract_and_store_jd
from app.services.jd_parser import extract_jd_data

router = APIRouter()

@router.post("/parse_jd", response_model=JDResponse)
def parse_jd(request: JDRequest, db: Session = Depends(get_db)):
    jd = extract_and_store_jd(request.jd_text, request.interviewer_ids, db)
    if jd is None:
        raise HTTPException(status_code=500, detail="Failed to extract JD.")
    return JDResponse(
        id=jd.id,
        job_title=jd.job_title,
        qualifications=jd.qualifications,
        location=jd.location,
        experience_required=jd.experience_required,
        required_skills=jd.required_skills.split(", ") if jd.required_skills else [],
        job_type=jd.job_type,
        company_name=jd.company_name,
        raw_jd_text=jd.raw_jd_text,
        interviewer_ids=[interviewer.id for interviewer in jd.interviewers]
    )

@router.get("/getJobDescriptions", response_model=List[JDResponse])
def get_job_descriptions(db: Session = Depends(get_db)):
    try:
        job_descriptions = db.query(JobDescription).all()
        return [
            JDResponse(
                id=jd.id,
                job_title=jd.job_title,
                qualifications=jd.qualifications,
                location=jd.location,
                experience_required=jd.experience_required,
                required_skills=jd.required_skills.split(", ") if jd.required_skills else [],
                job_type=jd.job_type,
                company_name=jd.company_name,
                raw_jd_text=jd.raw_jd_text,
                interviewer_ids=[interviewer.id for interviewer in jd.interviewers]
            )
            for jd in job_descriptions
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching job descriptions: {str(e)}"
        )

@router.put("/updateJobDescription/{jd_id}", response_model=JDResponse)
def update_job_description(jd_id: int, update_data: JDUpdateRequest, db: Session = Depends(get_db)):
    try:
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if not jd:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found"
            )

        if update_data.job_title is not None:
            jd.job_title = update_data.job_title
        if update_data.qualifications is not None:
            jd.qualifications = update_data.qualifications
        if update_data.location is not None:
            jd.location = update_data.location
        if update_data.experience_required is not None:
            jd.experience_required = update_data.experience_required
        if update_data.required_skills is not None:
            jd.required_skills = ", ".join(update_data.required_skills)
        if update_data.job_type is not None:
            jd.job_type = update_data.job_type
        if update_data.company_name is not None:
            jd.company_name = update_data.company_name
        if update_data.raw_jd_text is not None:
            jd.raw_jd_text = update_data.raw_jd_text

        if update_data.interviewer_ids is not None:
            jd.interviewers.clear()
            interviewers = db.query(User).filter(User.id.in_(update_data.interviewer_ids)).all()
            jd.interviewers.extend(interviewers)

        db.commit()
        db.refresh(jd)

        return JDResponse(
            id=jd.id,
            job_title=jd.job_title,
            qualifications=jd.qualifications,
            location=jd.location,
            experience_required=jd.experience_required,
            required_skills=jd.required_skills.split(", ") if jd.required_skills else [],
            job_type=jd.job_type,
            company_name=jd.company_name,
            raw_jd_text=jd.raw_jd_text,
            interviewer_ids=[interviewer.id for interviewer in jd.interviewers]
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating job description: {str(e)}"
        )

@router.delete("/deleteJobDescription/{jd_id}")
def delete_job_description(jd_id: int, db: Session = Depends(get_db)):
    try:
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if not jd:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found"
            )

        db.delete(jd)
        db.commit()

        return {"message": "Job description deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting job description: {str(e)}"
        )
