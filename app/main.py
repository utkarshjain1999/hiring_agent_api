from fastapi import FastAPI, Depends
from app.api import auth, resume_screener  # Import route modules
from app.auth.dependencies import get_current_user  # Adjusted path (based on your folder structure)
from app.database import Base, engine
from app.routes import auth
from app.api import company as company_api
from app.api import interviewer
from app.api import job_description
from app.api import resumer_matcher
from app.api import hr
# from app.models import users, candidate  # Import all models to register with Base

app = FastAPI()

# Create all tables before the app starts serving requests
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Register route modules
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(resume_screener.router, prefix="/resume", tags=["Resume Screener"])
# app.include_router(resume_screener.router, prefix="/api")
app.include_router(company_api.router, prefix="/company", tags=["Company"])
app.include_router(interviewer.router, prefix="/interviewer", tags=["Interviewers"])
app.include_router(job_description.router, prefix="/api/job_description", tags=["Job Description"])
app.include_router(resumer_matcher.router, prefix="/resume-screener", tags=["Resume Screener"])
app.include_router(hr.router, prefix="/hr", tags=["HR Panel"])

# Example secure endpoint
@app.get("/secure-data")
def secure_data(user=Depends(get_current_user)):
    return {"user": user}
