from datetime import datetime, timedelta
from jose import jwt
from app.config import JWT_SECRET_KEY,  ACCESS_TOKEN_EXPIRE_MINUTES

if JWT_SECRET_KEY is None:
    raise ValueError("JWT_SECRET_KEY is not set. Check your .env file and environment variables.")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY)
    return encoded_jwt

def decode_access_token(token: str):
    payload = jwt.decode(token, JWT_SECRET_KEY)
    return payload