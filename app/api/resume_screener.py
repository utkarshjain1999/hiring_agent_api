from fastapi import APIRouter, UploadFile, File, HTTPException
from io import BytesIO

from app.services.resume_parser import process_zip_file

router = APIRouter()

@router.post("/upload_zip/")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are accepted")

    content = await file.read()
    zip_bytes = BytesIO(content)
    extracted = process_zip_file(zip_bytes)

    if not extracted:
        return {"success": False, "message": "No valid resumes were processed."}
    return {"success": True, "extracted": extracted}
