import pandas as pd
import numpy as np
import json
from fastapi import HTTPException
from sklearn.metrics.pairwise import cosine_similarity
from app.crud.candidate import add_candidate_to_db, update_candidate_status, fetch_candidates, fetch_latest_resumes
from app.schemas.resume_candidate import MatchingRequest, CandidateData
from io import BytesIO
import re
import pandas as pd
from sqlalchemy.orm import Session
from app.models.job_description import JobDescription
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings

def clean_skills_string(skill_str):
    """Convert stringified set to a clean space-separated string"""
    # Remove curly braces and split by commas
    if isinstance(skill_str, str):
        skill_list = re.sub(r"[\{\}]", "", skill_str).split(",")
        return " ".join([s.strip() for s in skill_list if s.strip()])
    return ""

def fetch_jd_text_by_id(db: Session, jd_id: int) -> str:
    jd_row = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd_row:
        raise HTTPException(status_code=404, detail="Job description not found")
    return jd_row.raw_jd_text

def match_resumes_service(request: MatchingRequest, db: Session):
    print(f"[DEBUG] MatchingRequest batch_id: {request.batch_id}")
    stored_df = fetch_latest_resumes(db, batch_id=request.batch_id)
    print(f"[DEBUG] Resumes fetched count: {len(stored_df)}")
    if stored_df.empty:
        raise HTTPException(status_code=404, detail="No resumes found")

    parsed_dicts = stored_df["parsed_json"].apply(json.loads)
    parsed_df = pd.DataFrame(parsed_dicts.tolist())
    parsed_df["filename"] = stored_df["filename"].values
    parsed_df["skills"] = parsed_df["skills"].apply(clean_skills_string)
    parsed_df["experience"] = pd.to_numeric(parsed_df.get("experience", 0), errors="coerce").fillna(0).astype(int)
    parsed_df["Intern_Experience"] = pd.to_numeric(parsed_df.get("Intern_Experience", 0), errors="coerce").fillna(0).astype(int)
    parsed_df["graduation_year"] = parsed_df.get("graduation_year", "").astype(str)
    parsed_df["college"] = parsed_df.get("college", "")
    parsed_df["combined_text"] = parsed_df.apply(lambda row: f"{row['skills']} {row['experience']} {row['Intern_Experience']} {row['graduation_year']} {row['college']}", axis=1)

    top_matches = get_top_matching_resumes(parsed_df, request.jd_id, request.threshold, request.top_n, db)
    print(top_matches.head())
    if top_matches.empty:
        return {"matches": [], "message": "No suitable matches found"}

    for _, row in top_matches.iterrows():
        if row.get("email"):
            add_candidate_to_db(row.get("name", ""), row.get("phone", ""), row.get("email", ""))

    return {"matches": top_matches.to_dict(orient="records"), "count": len(top_matches)}

def get_top_matching_resumes(df, jd_id, threshold, top_n, db: Session):
    jd_text = fetch_jd_text_by_id(db, jd_id)
    df["combined_text"] = df["combined_text"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    jd_vector = np.array(embedding_model.embed_documents([jd_text])[0]).reshape(1, -1)
    resume_vectors = np.array(embedding_model.embed_documents(df["combined_text"].tolist()))
    similarities = cosine_similarity(jd_vector, resume_vectors)[0]
    df["similarity_score"] = similarities
    print(threshold)
    print(df.head())

    df1 = df[df["similarity_score"] > threshold].sort_values(by="similarity_score", ascending=False).head(top_n)
    print(df1.head())


    return df[df["similarity_score"] > threshold].sort_values(by="similarity_score", ascending=False).head(top_n)

def shortlist_candidate(data: CandidateData):
    return update_candidate_status(data.email, "shortlisted")

def hold_candidate(data: CandidateData):
    return update_candidate_status(data.email, "hold")

def reject_candidate(data: CandidateData):
    return update_candidate_status(data.email, "rejected")

def get_candidates_by_status(status, search):
    return fetch_candidates(status, search)

def export_candidates_to_excel():
    # Convert to Excel and return as bytes
    df = fetch_candidates("all")
    if df.empty:
        raise HTTPException(status_code=404, detail="No candidates found")
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output.getvalue()
