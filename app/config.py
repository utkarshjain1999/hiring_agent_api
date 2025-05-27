import os
from dotenv import load_dotenv

load_dotenv()

# JWT Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database Settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:uj%4097531322@localhost:5432/test")

# GROQ API Settings
GROQ_API_KEYS = [key.strip() for key in os.getenv("GROQ_API_KEYS", "").split(",") if key.strip()]
