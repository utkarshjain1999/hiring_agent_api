from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.company import CompanyCreate, CompanyOut
from app.crud import company as company_crud
from app.database import get_db

router = APIRouter()

@router.post("/register", response_model=CompanyOut)
def register_company(company: CompanyCreate, db: Session = Depends(get_db)):
    existing = company_crud.get_company_by_email(db, company.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this email already exists."
        )
    return company_crud.create_company(db, company)