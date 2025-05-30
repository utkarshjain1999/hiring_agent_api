from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.users import User
from app.schemas.company import CompanyCreate
from fastapi import HTTPException, status

def get_company_by_email(db: Session, email: str):
    return db.query(Company).filter(Company.email == email).first()

def get_company_by_domain(db: Session, domain: str):
    return db.query(Company).filter(Company.domain == domain).first()

def get_company_by_phone(db: Session, phone_number: str):
    if phone_number is None:
        return None
    return db.query(Company).filter(Company.phone_number == phone_number).first()

def create_company(db: Session, company: CompanyCreate):
    # Check for existing email
    existing_email = get_company_by_email(db, company.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this email already exists."
        )
    
    # Check for existing domain
    existing_domain = get_company_by_domain(db, company.domain)
    if existing_domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this domain already exists."
        )
    
    # Check for existing phone number if provided
    if company.phone_number:
        existing_phone = get_company_by_phone(db, company.phone_number)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this phone number already exists."
            )
    
    # Create company entry
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    
    # Create corresponding user entry
    try:
        # Check if user with same email already exists
        existing_user = db.query(User).filter(User.email == company.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists."
            )
        
        # Create new user with admin role
        new_user = User(
            name=company.full_name,  # Using company.full_name as the user's name
            email=company.email,
            phone_number=company.phone_number,  # phone_number is now required
            role="admin"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
    except Exception as e:
        # If user creation fails, rollback company creation
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user account: {str(e)}"
        )
    
    return db_company