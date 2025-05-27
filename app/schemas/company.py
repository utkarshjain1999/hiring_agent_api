from pydantic import BaseModel, EmailStr

class CompanyCreate(BaseModel):
    name: str
    domain: str
    full_name: str
    phone_number: str
    email: EmailStr
    designation: str

class CompanyOut(BaseModel):
    comp_id: int
    name: str
    domain: str
    full_name: str
    phone_number: str
    email: EmailStr
    designation: str

    class Config:
        orm_mode = True
