from sqlalchemy import Table, Column, ForeignKey
from app.database import Base

# Association table for job descriptions and interviewers
job_interviewers = Table(
    "job_interviewers",
    Base.metadata,
    Column("job_description_id", ForeignKey("job_descriptions.id"), primary_key=True),
    Column("interviewer_id", ForeignKey("users.id"), primary_key=True)
) 