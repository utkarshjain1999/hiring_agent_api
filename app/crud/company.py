from sqlalchemy.orm import Session
from app.models.company import Company
from app.schemas.company import CompanyCreate

def create_company(db: Session, company: CompanyCreate):
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def get_company_by_email(db: Session, email: str):
    return db.query(Company).filter(Company.email == email).first()