import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.candidate import (
    Candidate,
    PersonalInfo,
    EmploymentHistory,
    Skill,
    Education,
    Project,
    Certification,
    AdditionalInfo
)
from app.schemas.candidate_schema import CandidateProfile, CandidateUpdatePayload
from app.services.export_service import ExportService
from app.services.timeline import calculate_total_experience_years

router = APIRouter(prefix="/candidates", tags=["Candidates"])

def build_candidate_profile_dict(c: Candidate) -> dict:
    """Helper to reconstruct complete CandidateProfile dictionary from ORM models."""
    p_info = c.personal_info
    confidence_dict = {}
    if p_info and p_info.confidence_scores_json:
        try:
            confidence_dict = json.loads(p_info.confidence_scores_json)
        except Exception:
            pass

    personal_data = {
        "full_name": p_info.full_name if p_info else None,
        "email": p_info.email if p_info else None,
        "phone": p_info.phone if p_info else None,
        "location": p_info.location if p_info else None,
        "linkedin": p_info.linkedin if p_info else None,
        "github": p_info.github if p_info else None,
        "portfolio": p_info.portfolio if p_info else None,
        "confidence": confidence_dict
    }

    # Group skills by category
    skills_categorized = {
        "programming_languages": [],
        "frameworks": [],
        "libraries": [],
        "databases": [],
        "cloud": [],
        "ai_ml": [],
        "tools": [],
        "other_skills": []
    }
    for s in c.skills:
        cat = s.category if s.category in skills_categorized else "other_skills"
        skills_categorized[cat].append(s.normalized_name)

    # History
    history_list = []
    for h in c.employment_history:
        history_list.append({
            "id": h.id,
            "company_name": h.company_name,
            "job_title": h.job_title,
            "start_date": h.start_date,
            "end_date": h.end_date,
            "is_current": h.is_current,
            "duration_months": h.duration_months,
            "responsibilities": h.responsibilities,
            "confidence_score": h.confidence_score
        })

    # Education
    edu_list = []
    for e in c.education:
        edu_list.append({
            "id": e.id,
            "degree": e.degree,
            "institution": e.institution,
            "university": e.university,
            "specialization": e.specialization,
            "graduation_year": e.graduation_year,
            "score": e.score,
            "confidence_score": e.confidence_score
        })

    # Projects
    proj_list = []
    for p in c.projects:
        proj_list.append({
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "technologies": p.technologies,
            "link": p.link,
            "confidence_score": p.confidence_score
        })

    # Certs
    cert_list = []
    for cert in c.certifications:
        cert_list.append({
            "id": cert.id,
            "name": cert.name,
            "issuer": cert.issuer,
            "issue_date": cert.issue_date,
            "confidence_score": cert.confidence_score
        })

    # Additional
    langs = [a.title for a in c.additional_info if a.info_type == "language"]
    achievements = [a.description for a in c.additional_info if a.info_type == "achievement"]
    internships = [
        {"id": a.id, "info_type": "internship", "title": a.title, "description": a.description}
        for a in c.additional_info if a.info_type == "internship"
    ]

    # Missing fields
    missing = []
    if not personal_data.get("full_name"):
        missing.append("full_name")
    if not personal_data.get("email"):
        missing.append("email")
    if not personal_data.get("phone"):
        missing.append("phone")
    if not personal_data.get("location"):
        missing.append("location")
    if not personal_data.get("linkedin"):
        missing.append("linkedin")
    if not history_list:
        missing.append("employment_history")
    if not edu_list:
        missing.append("education")
    if not c.summary:
        missing.append("summary")

    return {
        "id": c.id,
        "resume_id": c.resume_id,
        "personal_information": personal_data,
        "professional_information": {
            "summary": c.summary,
            "total_experience_years": c.total_experience_years,
            "current_company": c.current_company,
            "current_job_title": c.current_job_title,
            "employment_history": history_list
        },
        "skills": skills_categorized,
        "education": edu_list,
        "projects": proj_list,
        "certifications": cert_list,
        "internships": internships,
        "achievements": achievements,
        "languages": langs,
        "missing_fields": missing,
        "overall_confidence": c.overall_confidence,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None
    }

@router.get("/", response_model=list[dict])
def list_candidates(db: Session = Depends(get_db)):
    """Lists summary of all candidate profiles."""
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    results = []
    for c in candidates:
        name = c.personal_info.full_name if c.personal_info else "Unnamed Candidate"
        email = c.personal_info.email if c.personal_info else None
        phone = c.personal_info.phone if c.personal_info else None
        results.append({
            "id": c.id,
            "resume_id": c.resume_id,
            "full_name": name,
            "email": email,
            "phone": phone,
            "current_job_title": c.current_job_title,
            "current_company": c.current_company,
            "total_experience_years": c.total_experience_years,
            "overall_confidence": c.overall_confidence,
            "created_at": c.created_at.isoformat() if c.created_at else None
        })
    return results

@router.get("/{candidate_id}", response_model=CandidateProfile)
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Retrieves full candidate profile."""
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return build_candidate_profile_dict(c)

@router.put("/{candidate_id}", response_model=CandidateProfile)
def update_candidate(
    candidate_id: str,
    payload: CandidateUpdatePayload,
    db: Session = Depends(get_db)
):
    """
    Updates candidate profile with user edits and corrections.
    Recalculates experience and confidence scores.
    """
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Update Personal Info
    if payload.personal_information and c.personal_info:
        p = payload.personal_information
        if p.full_name is not None:
            c.personal_info.full_name = p.full_name
        if p.email is not None:
            c.personal_info.email = p.email
        if p.phone is not None:
            c.personal_info.phone = p.phone
        if p.location is not None:
            c.personal_info.location = p.location
        if p.linkedin is not None:
            c.personal_info.linkedin = p.linkedin
        if p.github is not None:
            c.personal_info.github = p.github
        if p.portfolio is not None:
            c.personal_info.portfolio = p.portfolio

    # Update Professional Info
    if payload.professional_information:
        prof = payload.professional_information
        if prof.summary is not None:
            c.summary = prof.summary
        if prof.current_company is not None:
            c.current_company = prof.current_company
        if prof.current_job_title is not None:
            c.current_job_title = prof.current_job_title

        # Replace employment history records
        if prof.employment_history is not None:
            db.query(EmploymentHistory).filter(EmploymentHistory.candidate_id == candidate_id).delete()
            history_dicts = []
            for idx, job in enumerate(prof.employment_history):
                db_emp = EmploymentHistory(
                    candidate_id=candidate_id,
                    company_name=job.company_name,
                    job_title=job.job_title,
                    start_date=job.start_date,
                    end_date=job.end_date,
                    is_current=job.is_current,
                    duration_months=job.duration_months,
                    responsibilities=job.responsibilities,
                    confidence_score=job.confidence_score,
                    sort_order=idx
                )
                db.add(db_emp)
                history_dicts.append({
                    "start_date": job.start_date,
                    "end_date": job.end_date
                })
            # Recalculate overlap-free total experience
            c.total_experience_years = calculate_total_experience_years(history_dicts)

    # Update Skills
    if payload.skills:
        db.query(Skill).filter(Skill.candidate_id == candidate_id).delete()
        skills_dict = payload.skills.model_dump()
        for cat, skill_names in skills_dict.items():
            for name in skill_names:
                db.add(Skill(
                    candidate_id=candidate_id,
                    category=cat,
                    skill_name=name,
                    normalized_name=name,
                    confidence_score=1.0  # Manually verified/edited = 1.0
                ))

    # Update Education
    if payload.education is not None:
        db.query(Education).filter(Education.candidate_id == candidate_id).delete()
        for e in payload.education:
            db.add(Education(
                candidate_id=candidate_id,
                degree=e.degree,
                institution=e.institution,
                university=e.university,
                specialization=e.specialization,
                graduation_year=e.graduation_year,
                score=e.score,
                confidence_score=e.confidence_score
            ))

    # Update Projects
    if payload.projects is not None:
        db.query(Project).filter(Project.candidate_id == candidate_id).delete()
        for proj in payload.projects:
            db.add(Project(
                candidate_id=candidate_id,
                title=proj.title,
                description=proj.description,
                technologies=proj.technologies,
                link=proj.link,
                confidence_score=proj.confidence_score
            ))

    # Update Certifications
    if payload.certifications is not None:
        db.query(Certification).filter(Certification.candidate_id == candidate_id).delete()
        for cert in payload.certifications:
            db.add(Certification(
                candidate_id=candidate_id,
                name=cert.name,
                issuer=cert.issuer,
                issue_date=cert.issue_date,
                confidence_score=cert.confidence_score
            ))

    db.commit()
    db.refresh(c)
    return build_candidate_profile_dict(c)

@router.get("/{candidate_id}/export/json")
def export_candidate_json(candidate_id: str, db: Session = Depends(get_db)):
    """Exports candidate profile as structured JSON."""
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    data = build_candidate_profile_dict(c)
    candidate_name = (data["personal_information"].get("full_name") or "Candidate").replace(" ", "_")
    filename = f"{candidate_name}_profile.json"
    
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/{candidate_id}/export/excel")
def export_candidate_excel(candidate_id: str, db: Session = Depends(get_db)):
    """Exports candidate profile as styled multi-sheet Excel (.xlsx) workbook."""
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    data = build_candidate_profile_dict(c)
    candidate_name = (data["personal_information"].get("full_name") or "Candidate").replace(" ", "_")
    filename = f"{candidate_name}_profile.xlsx"

    excel_stream = ExportService.generate_excel(data)
    
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

