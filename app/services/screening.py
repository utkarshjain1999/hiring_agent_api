import pandas as pd
import numpy as np
import json
from fastapi import HTTPException
from sklearn.metrics.pairwise import cosine_similarity
from app.crud.candidate import add_candidate_to_db, update_candidate_status, fetch_candidates, fetch_latest_resumes
from app.schemas.resume_candidate import MatchingRequest, CandidateData
from app.models.candidate import Candidate
from app.database import get_db
from io import BytesIO
import re
import pandas as pd
from sqlalchemy.orm import Session
from app.models.job_description import JobDescription
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy.exc import IntegrityError
from fastapi.responses import StreamingResponse
from datetime import datetime

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

def fetch_candidates_by_jd(jd_id: int,db: Session):
    candidates = db.query(Candidate).filter(Candidate.jd_id == jd_id).all()
    grouped = {"new": [], "shortlisted": [], "hold": [], "rejected": []}
    for c in candidates:
        grouped.setdefault(c.status, []).append(c.to_dict())
    return grouped


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
    parsed_df["resume_id"] = stored_df["resume_id"].values  # ✅ Carry over resume_id
    parsed_df["jd_id"] = request.jd_id
    parsed_df["combined_text"] = parsed_df.apply(lambda row: f"{row['skills']} {row['experience']} {row['Intern_Experience']} {row['graduation_year']} {row['college']}", axis=1)

    top_matches = get_top_matching_resumes(parsed_df, request.jd_id, request.threshold, request.top_n, db)
    print(top_matches.head())
    if top_matches.empty:
        return {"matches": [], "message": "No suitable matches found"}

    for _, row in top_matches.iterrows():
        if row.get("email"):
            print("[DEBUG] Resume ID for candidate:", row.get("resume_id"))
            try:
                add_candidate_to_db(
                    row.get("name", ""),
                    row.get("phone_number", ""),
                    row.get("email", ""),
                    row.get("resume_id"),
                    request.jd_id
                )
            except IntegrityError:
                db.rollback()
                print(f"[INFO] Candidate with email {row.get('email')} already exists. Skipping insert.")

    return fetch_candidates_by_jd(request.jd_id,db)
    # return {"matches": top_matches.to_dict(orient="records"), "count": len(top_matches)}

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

# def shortlist_candidate(data: CandidateData):
#     return update_candidate_status(data.email, "shortlisted")
#
# def hold_candidate(data: CandidateData):
#     return update_candidate_status(data.email, "hold")
#
# def reject_candidate(data: CandidateData):
#     return update_candidate_status(data.email, "rejected")

def update_candidate_status_by_resume(resume_id, status):
    db = next(get_db())
    candidate = db.query(Candidate).filter(Candidate.resume_id == resume_id).first()
    if candidate:
        candidate.status = status
        if status.lower() == 'shortlisted':
            candidate.shortlisted_date = datetime.utcnow()  # or .now() for local time
        db.commit()
        return {"success": True}
        db.commit()
        return {"success": True}
    raise HTTPException(status_code=404, detail="Candidate not found")


def get_candidates_by_status(payload: dict):
    jd_id = payload.get("jdId")
    search_query = payload.get("searchQuery", None)

    if not jd_id:
        raise HTTPException(status_code=400, detail="jdId is required")

    return fetch_candidates(jd_id=jd_id, search=search_query)

def export_candidates_to_excel(jd_id: int):
    grouped = fetch_candidates(jd_id)

    all_candidates = []
    for status, candidates in grouped.items():
        for c in candidates:
            c["status"] = status  # Ensure status is included
            all_candidates.append(c)

    df = pd.DataFrame(all_candidates)

    print("[DEBUG] DataFrame Preview:")
    print(df.head())
    print("[DEBUG] DataFrame dtypes:")
    print(df.dtypes)

    if df.empty:
        raise HTTPException(status_code=404, detail="No candidates found")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    filename = f"Candidates-{jd_id}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

