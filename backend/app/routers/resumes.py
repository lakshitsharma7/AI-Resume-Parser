import os
import time
import uuid
import json
import logging
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.resume import Resume
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
from app.schemas.candidate_schema import ResumeUploadResponse, CandidateProfile
from app.schemas.resume_parse_schema import (
    ResumeParseResponse,
    ParseAndSendResponse,
    ParsedCandidateData,
    ParsingMetadata,
    ForwardingResult
)
from app.services.extractor import DocumentExtractor
from app.services.nlp_parser import NLPResumeParser
from app.services.ollama_client import OllamaClient
from app.services.merger import ResumeMerger
from app.services.forwarder import DestinationForwarder

router = APIRouter(prefix="/resumes", tags=["Resumes"])
logger = logging.getLogger(__name__)

async def _extract_and_parse(file: UploadFile) -> Tuple[ParsedCandidateData, ParsingMetadata]:
    """
    Core extraction worker: reads file, extracts text, runs dual parsing pipeline,
    validates with Pydantic, and ensures the temporary file is deleted immediately.
    """
    filename = file.filename or "unknown_resume"
    ext = Path(filename).suffix.lower()

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    file_content = await file.read()
    file_size = len(file_content)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty (0 bytes)."
        )

    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    # Create temporary file with guaranteed cleanup
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=ext)
    start_time = time.time()
    try:
        with os.fdopen(tmp_fd, "wb") as f:
            f.write(file_content)

        # Step 1: Text Extraction (Column-Aware & OCR-Capable)
        try:
            extracted_text, extract_engine = DocumentExtractor.extract_text(tmp_path)
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Document parsing error: {str(e)}")

        if not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to extract text from document. Ensure scanned files have legible text."
            )

        # Step 2: Deterministic Rule & spaCy NLP Parsing
        nlp_data = NLPResumeParser.parse(extracted_text)

        # Step 3: Local AI Processing via Ollama (if available)
        llm_data = None
        engine_used = "spacy_rule"
        ollama_status = OllamaClient.check_availability()
        if ollama_status["available"] and ollama_status["model_ready"]:
            llm_data = OllamaClient.extract_with_llm(extracted_text)
            if llm_data:
                engine_used = "hybrid"

        # Step 4: Fusion & Grounding Validation
        candidate_data = ResumeMerger.merge(nlp_data, llm_data, raw_text=extracted_text)

        # Map to ParsedCandidateData schema
        p_info = candidate_data.get("personal_information", {})
        personal_model = {
            "name": p_info.get("name") or p_info.get("full_name"),
            "email": p_info.get("email"),
            "phone": p_info.get("phone"),
            "location": p_info.get("location"),
            "linkedin": p_info.get("linkedin"),
            "github": p_info.get("github"),
            "portfolio": p_info.get("portfolio")
        }

        # Work Experience
        work_list = []
        for j in candidate_data.get("work_experience", []):
            work_list.append({
                "company": j.get("company") or j.get("company_name", "Unknown"),
                "designation": j.get("designation") or j.get("job_title", "Professional"),
                "start_date": j.get("start_date"),
                "end_date": j.get("end_date"),
                "is_current": j.get("is_current", False),
                "duration_months": j.get("duration_months", 0),
                "responsibilities": j.get("responsibilities")
            })

        # Education
        edu_list = []
        for e in candidate_data.get("education", []):
            edu_list.append({
                "institution": e.get("institution") or e.get("university"),
                "degree": e.get("degree"),
                "field": e.get("field") or e.get("specialization"),
                "start_year": e.get("start_year"),
                "end_year": e.get("end_year") or e.get("graduation_year")
            })

        # Projects
        proj_list = []
        for p in candidate_data.get("projects", []):
            proj_list.append({
                "name": p.get("name") or p.get("title", "Project"),
                "description": p.get("description"),
                "technologies": p.get("technologies"),
                "link": p.get("link")
            })

        # Certifications
        cert_list = []
        for c in candidate_data.get("certifications", []):
            cert_list.append({
                "name": c.get("name", "Certification"),
                "issuer": c.get("issuer"),
                "issue_date": str(c.get("issue_date", "")) if c.get("issue_date") else None
            })

        parsed_model = ParsedCandidateData(
            personal_information=personal_model,
            professional_summary=candidate_data.get("professional_summary") or candidate_data.get("professional_information", {}).get("summary"),
            skills=candidate_data.get("skills", {}),
            work_experience=work_list,
            education=edu_list,
            projects=proj_list,
            certifications=cert_list,
            languages=candidate_data.get("languages", []),
            total_experience_months=candidate_data.get("total_experience_months", 0),
            total_experience_years=candidate_data.get("total_experience_years", 0.0),
            confidence_and_evidence=candidate_data.get("confidence_and_evidence", {})
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        metadata = ParsingMetadata(
            engine=engine_used,
            duration_ms=elapsed_ms,
            file_type=ext,
            file_size_bytes=file_size
        )
        return parsed_model, metadata

    finally:
        # Guarantee no permanent storage of uploaded resumes
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

@router.post("/parse", response_model=ResumeParseResponse, status_code=status.HTTP_200_OK)
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse a resume file (PDF, DOCX, or scanned PDF) and return structured, validated JSON.
    Calculates non-overlapping career experience in months and years.
    Does not permanently store the uploaded file by default.
    """
    parsed_data, metadata = await _extract_and_parse(file)
    return ResumeParseResponse(
        status="success",
        data=parsed_data,
        metadata=metadata
    )

@router.post("/parse-and-send", response_model=ParseAndSendResponse, status_code=status.HTTP_200_OK)
async def parse_and_send_resume(
    file: UploadFile = File(...),
    destination_url: str = Form(..., description="Target API endpoint URL to receive parsed JSON"),
    auth_token: Optional[str] = Form(None, description="Optional bearer token or API key"),
    auth_header_name: str = Form("Authorization", description="Header name for authentication"),
    auth_scheme: Optional[str] = Form("Bearer", description="Authentication scheme (e.g. Bearer)"),
    custom_headers: Optional[str] = Form(None, description="Optional custom headers as JSON string")
):
    """
    Parse a resume and immediately forward the validated candidate JSON to a destination API.
    Enforces strict SSRF protection, request timeouts, and token masking.
    """
    parsed_data, metadata = await _extract_and_parse(file)

    # Convert Pydantic model to clean serializable dict
    payload_dict = parsed_data.model_dump()

    # Forward to destination
    success, status_code, response_body, forward_ms, masked_auth = await DestinationForwarder.forward_json(
        payload=payload_dict,
        destination_url=destination_url,
        auth_token=auth_token,
        auth_header_name=auth_header_name,
        auth_scheme=auth_scheme,
        custom_headers_json=custom_headers
    )

    forwarding_result = ForwardingResult(
        destination_url=destination_url,
        destination_status_code=status_code,
        destination_response=response_body,
        forwarding_duration_ms=forward_ms,
        masked_auth_header=masked_auth
    )

    resp_status = "success" if success else "forwarding_error"
    return ParseAndSendResponse(
        status=resp_status,
        parsed_resume=parsed_data,
        forwarding=forwarding_result,
        metadata=metadata
    )

@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_parse_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Uploads a resume file and saves to SQLite database for the interactive UI dashboard.
    """
    filename = file.filename or "unknown_resume"
    ext = Path(filename).suffix.lower()

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = settings.UPLOADS_DIR / stored_name

    file_content = await file.read()
    file_size = len(file_content)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty (0 bytes)."
        )

    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    with open(stored_path, "wb") as f:
        f.write(file_content)

    # Create Resume DB Record
    db_resume = Resume(
        original_filename=filename,
        stored_filename=stored_name,
        file_path=str(stored_path),
        file_size=file_size,
        file_type=ext,
        parsing_status="PROCESSING"
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)

    try:
        extracted_text, extract_engine = DocumentExtractor.extract_text(str(stored_path))
        db_resume.extracted_text = extracted_text

        if not extracted_text.strip():
            db_resume.parsing_status = "FAILED"
            db_resume.error_message = "No readable text could be extracted from document."
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to extract any text from resume. Ensure scanned documents have legible text."
            )

        nlp_data = NLPResumeParser.parse(extracted_text)

        llm_data = None
        engine_used = "spacy_rule"
        ollama_status = OllamaClient.check_availability()
        if ollama_status["available"] and ollama_status["model_ready"]:
            llm_data = OllamaClient.extract_with_llm(extracted_text)
            if llm_data:
                engine_used = "hybrid"

        candidate_data = ResumeMerger.merge(nlp_data, llm_data, raw_text=extracted_text)

        db_candidate = Candidate(
            resume_id=db_resume.id,
            total_experience_years=candidate_data["professional_information"]["total_experience_years"],
            summary=candidate_data["professional_information"]["summary"],
            current_company=candidate_data["professional_information"]["current_company"],
            current_job_title=candidate_data["professional_information"]["current_job_title"],
            overall_confidence=candidate_data["overall_confidence"]
        )
        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)

        # Personal Info
        p_info = candidate_data["personal_information"]
        db_pinfo = PersonalInfo(
            candidate_id=db_candidate.id,
            full_name=p_info.get("full_name") or p_info.get("name"),
            email=p_info.get("email"),
            phone=p_info.get("phone"),
            location=p_info.get("location"),
            linkedin=p_info.get("linkedin"),
            github=p_info.get("github"),
            portfolio=p_info.get("portfolio"),
            confidence_scores_json=json.dumps(p_info.get("confidence", {}))
        )
        db.add(db_pinfo)

        # Employment History
        for idx, job in enumerate(candidate_data["professional_information"]["employment_history"]):
            db_emp = EmploymentHistory(
                candidate_id=db_candidate.id,
                company_name=job.get("company_name") or job.get("company", "Unknown Company"),
                job_title=job.get("job_title") or job.get("designation", "Professional"),
                start_date=job.get("start_date"),
                end_date=job.get("end_date"),
                is_current=job.get("is_current", False),
                duration_months=job.get("duration_months", 0),
                responsibilities=job.get("responsibilities"),
                confidence_score=job.get("confidence_score", 0.85),
                sort_order=idx
            )
            db.add(db_emp)

        # Skills
        for category, skill_list in candidate_data["skills"].items():
            for s_name in skill_list:
                db_skill = Skill(
                    candidate_id=db_candidate.id,
                    category=category,
                    skill_name=s_name,
                    normalized_name=s_name,
                    confidence_score=0.92
                )
                db.add(db_skill)

        # Education
        for edu in candidate_data["education"]:
            db_edu = Education(
                candidate_id=db_candidate.id,
                degree=edu.get("degree"),
                institution=edu.get("institution") or edu.get("university"),
                university=edu.get("university") or edu.get("institution"),
                specialization=edu.get("specialization") or edu.get("field"),
                graduation_year=str(edu.get("graduation_year") or edu.get("end_year") or ""),
                score=edu.get("score"),
                confidence_score=edu.get("confidence_score", 0.85)
            )
            db.add(db_edu)

        # Projects
        for proj in candidate_data["projects"]:
            db_proj = Project(
                candidate_id=db_candidate.id,
                title=proj.get("title") or proj.get("name", "Project"),
                description=proj.get("description"),
                technologies=proj.get("technologies"),
                link=proj.get("link"),
                confidence_score=proj.get("confidence_score", 0.85)
            )
            db.add(db_proj)

        # Certifications
        for cert in candidate_data["certifications"]:
            db_cert = Certification(
                candidate_id=db_candidate.id,
                name=cert.get("name", "Certification"),
                issuer=cert.get("issuer"),
                issue_date=str(cert.get("issue_date", "")),
                confidence_score=cert.get("confidence_score", 0.90)
            )
            db.add(db_cert)

        # Languages & Achievements
        for lang in candidate_data.get("languages", []):
            db_add = AdditionalInfo(
                candidate_id=db_candidate.id,
                info_type="language",
                title=lang,
                description=""
            )
            db.add(db_add)

        for ach in candidate_data.get("achievements", []):
            db_add = AdditionalInfo(
                candidate_id=db_candidate.id,
                info_type="achievement",
                title="Achievement",
                description=ach
            )
            db.add(db_add)

        db_resume.parsing_status = "COMPLETED"
        db_resume.parsing_engine = engine_used
        db.commit()

        candidate_data["id"] = db_candidate.id
        candidate_data["resume_id"] = db_resume.id
        candidate_data["created_at"] = db_candidate.created_at.isoformat()

        return ResumeUploadResponse(
            status="success",
            resume_id=db_resume.id,
            candidate_id=db_candidate.id,
            parsing_engine=engine_used,
            parsing_status="COMPLETED",
            candidate=candidate_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error processing resume")
        db_resume.parsing_status = "FAILED"
        db_resume.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while parsing resume: {str(e)}"
        )

@router.get("/", response_model=list[dict])
def list_resumes(db: Session = Depends(get_db)):
    """Lists all uploaded resume records."""
    resumes = db.query(Resume).order_by(Resume.created_at.desc()).all()
    results = []
    for r in resumes:
        results.append({
            "id": r.id,
            "filename": r.original_filename,
            "file_size": r.file_size,
            "file_type": r.file_type,
            "parsing_engine": r.parsing_engine,
            "parsing_status": r.parsing_status,
            "candidate_id": r.candidate.id if r.candidate else None,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return results

@router.get("/{resume_id}", response_model=dict)
def get_resume(resume_id: str, db: Session = Depends(get_db)):
    """Retrieves resume metadata and raw extracted text."""
    r = db.query(Resume).filter(Resume.id == resume_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {
        "id": r.id,
        "filename": r.original_filename,
        "file_size": r.file_size,
        "file_type": r.file_type,
        "parsing_engine": r.parsing_engine,
        "parsing_status": r.parsing_status,
        "error_message": r.error_message,
        "extracted_text": r.extracted_text,
        "candidate_id": r.candidate.id if r.candidate else None,
        "created_at": r.created_at.isoformat() if r.created_at else None
    }

@router.delete("/{resume_id}")
def delete_resume(resume_id: str, db: Session = Depends(get_db)):
    """Deletes a resume and associated candidate records."""
    r = db.query(Resume).filter(Resume.id == resume_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if r.file_path and os.path.exists(r.file_path):
        try:
            os.remove(r.file_path)
        except Exception:
            pass

    db.delete(r)
    db.commit()
    return {"status": "success", "message": "Resume and candidate deleted"}
