import os
import tempfile
import zipfile
import random
import time
import json
from io import BytesIO
from typing import List, Optional
import pdfplumber
import docx
from app.models.resume import Resume
from app.database import SessionLocal
from langchain_groq import ChatGroq
from app.core.utils import extract_first_json  # Ensure this utility is available
from app.config import GROQ_API_KEYS
import uuid

# Load GROQ API keys from environment variable


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

def extract_text_from_file(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        try:
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    elif file_path.endswith(".docx"):
        try:
            doc = docx.Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""
    return ""

def query_groq_api(text: str, max_retries: int = 3) -> Optional[dict]:
    base_delay = 2
    retries = 0
    used_keys = set()

    while retries < max_retries and len(used_keys) < len(GROQ_API_KEYS):
        available_keys = [k for k in GROQ_API_KEYS if k not in used_keys]
        if not available_keys:
            break
        api_key = random.choice(available_keys)
        used_keys.add(api_key)

        llm = ChatGroq(
            temperature=0,
            groq_api_key=api_key,
            model_name="llama-3.1-8b-instant"
        )

        try:
            prompt = f"""
            You're an expert HR assistant. Extract the following details from the given resume text.
            Return output strictly in this JSON format:

            {{
              "name": "Full name of the candidate",
              "email": "Email address",
              "phone": "Contact number",
              "college": "Name of the college/university attended",
              "skills": ["skill1", "skill2", ...],
              "graduation_year": 2025,
              "certification": ["cert1", "cert2", ...],
              "experience": 0,
              "Intern_Experience": {{
                "duration_months": 0,
                "roles": ["role1", "role2", ...],
                "durations": ["2 months", "3 months"],
                "companies": ["Company A", "Company B"],
                "locations": ["onsite", "remote"]
              }}
            }}

            Resume Text:
            {text}
            """
            response = llm.invoke(prompt)
            raw_output = response.content.strip()
            parsed_response = extract_first_json(raw_output)
            if parsed_response:
                return parsed_response
        except Exception as e:
            print(f"API error: {e}")
            time.sleep(base_delay * (2 ** retries) + random.random())
            retries += 1
    return None

def process_zip_file(file: BytesIO) -> List[dict]:
    extracted_resumes = []
    batch_uuid = uuid.uuid4()
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with zipfile.ZipFile(file) as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            print("Uploaded file is not a valid zip file.")
            return extracted_resumes

        db = SessionLocal()
        for root, _, files in os.walk(temp_dir):
            for filename in files:
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext not in SUPPORTED_EXTENSIONS:
                    continue

                file_path = os.path.join(root, filename)
                text = extract_text_from_file(file_path)
                if not text.strip():
                    continue

                resume_data = query_groq_api(text)
                if resume_data:
                    resume_data["source_file"] = filename

                    resume_record = Resume(
                        name=resume_data.get("name"),
                        email=resume_data.get("email"),
                        phone=resume_data.get("phone"),
                        college=resume_data.get("college"),
                        graduation_year=resume_data.get("graduation_year"),
                        skills=resume_data.get("skills"),
                        certification=resume_data.get("certification"),
                        experience=resume_data.get("experience"),
                        intern_experience=resume_data.get("Intern_Experience"),
                        source_file=resume_data.get("source_file"),
                        batch_id = batch_uuid
                    )
                    db.add(resume_record)
                    db.commit()
                    db.refresh(resume_record)

                    extracted_resumes.append(resume_data)
        db.close()
    return {"batch_id": str(batch_uuid), "resumes": extracted_resumes}
