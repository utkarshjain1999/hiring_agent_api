from sqlalchemy.orm import Session
from app.models.users import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def update_user_password(db: Session, user: User, hashed_password: str):
    user.hashed_password = hashed_password
    db.commit()
    return user

def check_token_used(db: Session, email: str) -> bool:
    user = get_user_by_email(db, email)
    return user.password_setup_token_used if user else False 