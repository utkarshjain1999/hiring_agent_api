from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import re

# Phone number validation pattern
PHONE_PATTERN = r'^\+?1?\d{9,15}$'

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    phone_number: str = Field(..., pattern=PHONE_PATTERN)
    role: str = "candidate"

class PasswordSetupRequest(BaseModel):
    token: str
    password: str = Field(..., min_length=8)  # Minimum 8 characters for password

class PasswordSetupResponse(BaseModel):
    message: str
    email: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordResponse(BaseModel):
    message: str
    email: str

class ResetPasswordConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class ResetPasswordConfirmResponse(BaseModel):
    message: str
    email: str