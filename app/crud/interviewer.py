from sqlalchemy.orm import Session
from app.models.users import User
from app.schemas.interviewer import InterviewerCreate, InterviewerUpdate
from app.core.security import get_password_hash
from datetime import datetime
from app.models.interviewer import InterviewerAvailability
from app.schemas.interviewer import CreateSlot

def create_interviewer(db: Session, interviewer: InterviewerCreate):
    hashed_pw = get_password_hash(interviewer.password)
    db_user = User(
        username=interviewer.username,
        hashed_password=hashed_pw,
        role="interviewer"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_interviewers(db: Session):
    return db.query(User).filter(User.role == "interviewer").all()

def update_interviewer(db: Session, interviewer_id: int, updates: InterviewerUpdate):
    db_user = db.query(User).filter(User.id == interviewer_id, User.role == "interviewer").first()
    if not db_user:
        return None
    if updates.username:
        db_user.username = updates.username
    if updates.password:
        db_user.hashed_password = get_password_hash(updates.password)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_interviewer(db: Session, interviewer_id: int):
    db_user = db.query(User).filter(User.id == interviewer_id, User.role == "interviewer").first()
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

def create_availability_slot(db: Session, slot_data: CreateSlot):
    print('starting creating slot function..........')
    # Combine date + start_time and date + end_time into datetime objects
    start_datetime = datetime.combine(slot_data.date, slot_data.start_time)
    end_datetime = datetime.combine(slot_data.date, slot_data.end_time)

    # Debugging prints - add these lines
    print(f"Start timestamp type: {type(start_datetime)}")  # Should show <class 'datetime.datetime'>
    print(f"Start timestamp value: {start_datetime}")
    print(f"End timestamp type: {type(end_datetime)}")  # Should show <class 'datetime.datetime'>
    print(f"End timestamp value: {end_datetime}")

    new_slot = InterviewerAvailability(
        interviewer_id=slot_data.interviewer_id,
        date = slot_data.date,
        start_time=start_datetime,
        end_time=end_datetime
    )
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)
    return new_slot
