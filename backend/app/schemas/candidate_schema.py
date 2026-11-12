from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ConfidenceScores(BaseModel):
    full_name: float = 0.0
    email: float = 0.0
    phone: float = 0.0
    location: float = 0.0
    linkedin: float = 0.0
    github: float = 0.0
    portfolio: float = 0.0

class PersonalInfoBase(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    confidence: Optional[Dict[str, float]] = Field(default_factory=dict)

class EmploymentHistoryItem(BaseModel):
    id: Optional[str] = None
    company_name: str
    job_title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    duration_months: int = 0
    responsibilities: Optional[str] = None
    confidence_score: float = 0.85

class ProfessionalInfo(BaseModel):
    summary: Optional[str] = None
    total_experience_years: float = 0.0
    current_company: Optional[str] = None
    current_job_title: Optional[str] = None
    employment_history: List[EmploymentHistoryItem] = Field(default_factory=list)

class SkillsCategorized(BaseModel):
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    libraries: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud: List[str] = Field(default_factory=list)
    ai_ml: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    other_skills: List[str] = Field(default_factory=list)

class EducationItem(BaseModel):
    id: Optional[str] = None
    degree: Optional[str] = None
    institution: Optional[str] = None
    university: Optional[str] = None
    specialization: Optional[str] = None
    graduation_year: Optional[str] = None
    score: Optional[str] = None
    confidence_score: float = 0.85

class ProjectItem(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    technologies: Optional[str] = None
    link: Optional[str] = None
    confidence_score: float = 0.85

class CertificationItem(BaseModel):
    id: Optional[str] = None
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    confidence_score: float = 0.90

class AdditionalItem(BaseModel):
    id: Optional[str] = None
    info_type: str  # "internship", "achievement", "language"
    title: str
    description: Optional[str] = None

class CandidateProfile(BaseModel):
    id: Optional[str] = None
    resume_id: Optional[str] = None
    personal_information: PersonalInfoBase
    professional_information: ProfessionalInfo
    skills: SkillsCategorized
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    internships: List[AdditionalItem] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)
    overall_confidence: float = 0.0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class CandidateUpdatePayload(BaseModel):
    personal_information: Optional[PersonalInfoBase] = None
    professional_information: Optional[ProfessionalInfo] = None
    skills: Optional[SkillsCategorized] = None
    education: Optional[List[EducationItem]] = None
    projects: Optional[List[ProjectItem]] = None
    certifications: Optional[List[CertificationItem]] = None
    internships: Optional[List[AdditionalItem]] = None
    achievements: Optional[List[str]] = None
    languages: Optional[List[str]] = None

class ResumeUploadResponse(BaseModel):
    status: str
    resume_id: str
    candidate_id: Optional[str] = None
    parsing_engine: str
    parsing_status: str
    candidate: Optional[CandidateProfile] = None
    message: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    database: str
    ollama: Dict[str, Any]
    tesseract_ocr: Dict[str, Any]
    version: str

