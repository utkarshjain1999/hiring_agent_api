from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from app.models.users import User
from app.schemas.interviewer import InterviewerCreate, InterviewerUpdate
from datetime import datetime
from app.models.interviewer import InterviewerAvailability
from app.schemas.interviewer import CreateSlot

def create_interviewer(db: Session, interviewer: InterviewerCreate):
    # Check if email or phone number already exists
    existing_user = db.query(User).filter(
        (User.email == interviewer.email) | 
        (User.phone_number == interviewer.phone_number)
    ).first()
    
    if existing_user:
        raise ValueError("Email or phone number already registered")
    
    db_user = User(
        name=interviewer.name,
        email=interviewer.email,
        phone_number=interviewer.phone_number,
        role="interviewer"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_interviewers(db: Session):
    # Get all interviewers and filter out any that don't meet our schema requirements
    interviewers = db.query(User).filter(
        User.role == "interviewer",
        User.name.isnot(None),
        User.phone_number.isnot(None),
        User.email.isnot(None)
    ).all()
    
    # If any interviewer is missing required fields, we should log this
    invalid_interviewers = db.query(User).filter(
        User.role == "interviewer",
        (User.name.is_(None) | User.phone_number.is_(None) | User.email.is_(None))
    ).all()
    
    if invalid_interviewers:
        print(f"Warning: Found {len(invalid_interviewers)} interviewers with missing required fields")
        for interviewer in invalid_interviewers:
            print(f"Interviewer ID {interviewer.id}: name={interviewer.name}, phone={interviewer.phone_number}, email={interviewer.email}")
    
    return interviewers

def update_interviewer(db: Session, interviewer_id: int, updates: InterviewerUpdate):
    db_user = db.query(User).filter(User.id == interviewer_id, User.role == "interviewer").first()
    if not db_user:
        return None
        
    # Check if new email or phone number conflicts with existing users
    if updates.email or updates.phone_number:
        filters = [User.id != interviewer_id]

        if updates.email and updates.phone_number:
            filters.append(or_(
                User.email == updates.email,
                User.phone_number == updates.phone_number
            ))
        elif updates.email:
            filters.append(User.email == updates.email)
        elif updates.phone_number:
            filters.append(User.phone_number == updates.phone_number)

        existing_user = db.query(User).filter(and_(*filters)).first()

        if existing_user:
            raise ValueError("Email or phone number already registered")
    
    if updates.name:
        db_user.name = updates.name
    if updates.email:
        db_user.email = updates.email
    if updates.phone_number:
        db_user.phone_number = updates.phone_number
        
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_interviewer(db: Session, interviewer_id: int):
    # First, get the interviewer
    db_user = db.query(User).filter(User.id == interviewer_id, User.role == "interviewer").first()
    if not db_user:
        return None
    
    # Remove the interviewer from all job descriptions
    db_user.job_descriptions = []
    db.commit()
    
    # Now delete the user
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
