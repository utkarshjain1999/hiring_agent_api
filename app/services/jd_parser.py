import json
import re
import time
from langchain_groq import ChatGroq
from app.config import GROQ_API_KEYS  # import from config

def extract_jd_data(jd_text: str, max_retries: int = 4):
    prompt = f"""
    You're an expert HR assistant. Extract the following details from the job description below
    and return the output strictly in valid JSON format:

    {{
        "job_title": <Extracted Job Title or null>,
        "qualifications": <Extracted Degree or any>,
        "location": <Extracted Location or null>,
        "experience_required": <Experience Required (in years or months) or make it 0>,
        "required_skills": <List of Technical Skills or null>,
        "job_type": <Full-time/Part-time/Contract/Internship or null>,
        "company_name": <Extracted Company Name or null>
    }}

    Do not include explanations. Only provide structured JSON.

    Job Description: {jd_text}
    """

    for attempt in range(min(max_retries, len(GROQ_API_KEYS))):
        try:
            llm = ChatGroq(
                temperature=0,
                groq_api_key=GROQ_API_KEYS[attempt],
                model_name="llama-3.1-8b-instant"
            )
            response = llm.invoke(prompt).content.strip()
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"[Attempt {attempt + 1}] Failed with key {GROQ_API_KEYS[attempt][:10]}...: {e}")
            time.sleep(2 ** attempt)
    return None
