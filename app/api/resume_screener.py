from fastapi import APIRouter, UploadFile, File, HTTPException, UploadFile, File, Form, HTTPException, Depends
from io import BytesIO
from sqlalchemy.orm import Session
from app.services.resume_parser import process_zip_file
from app.database import get_db
from app.schemas.resume_candidate import MatchingRequest
from app.services.screening import match_resumes_service


router = APIRouter()

@router.post("/upload_zip/")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are accepted")

    content = await file.read()
    zip_bytes = BytesIO(content)
    extracted = process_zip_file(zip_bytes)

    if not extracted:
        return {"success": False, "message": "No valid resumes were processed.","batch_id": extracted["batch_id"]}
    return {"success": True, "extracted": extracted,"batch_id": extracted["batch_id"]}

@router.post("/upload_and_match")
async def upload_and_match(
    jdId: int = Form(...),
    threshold: float = Form(...),
    topMatches: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate ZIP file
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are accepted")

    # Process ZIP file
    content = await file.read()
    zip_bytes = BytesIO(content)
    extracted = process_zip_file(zip_bytes)

    if not extracted:
        return {
            "success": False,
            "message": "No valid resumes were processed.",
        }

    # Prepare matching request
    matching_request = MatchingRequest(
        jd_id=jdId,
        threshold=threshold,
        top_n=topMatches,
        batch_id=extracted["batch_id"]
    )

    resume_count = len(extracted["resumes"])
    print(f"✅ Matching will be performed against {resume_count} resumes.")
    # Match resumes
    # matches = match_resumes_service(matching_request, db)

    # return {
    #     "success": True,
    #     "message": "Resumes processed and matched successfully.",
    #     "batch_id": extracted["batch_id"],
    #     "matches": matches["matches"],
    #     "count": matches["count"]
    # }
    return match_resumes_service(matching_request, db)



