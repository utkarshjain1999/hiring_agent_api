from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from app.auth.jwt_handler import create_access_token
from app.schemas.users import LoginRequest, RegisterRequest
from app.models.users import User
from app.database import get_db

router = APIRouter()

@router.post("/login")
def login_user(login: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login.username).first()
    if not user or not bcrypt.verify(login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"sub": user.username, "role": user.role}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
def register_user(register: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == register.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    if register.role not in ["admin", "hr", "interviewer", "company_representative", "candidate"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    hashed_password = bcrypt.hash(register.password)
    new_user = User(username=register.username, hashed_password=hashed_password, role=register.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token_data = {"sub": new_user.username, "role": new_user.role}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}