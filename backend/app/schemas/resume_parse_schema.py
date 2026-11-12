from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class FieldConfidenceEvidence(BaseModel):
    confidence: float = Field(0.0, description="Extraction confidence score from 0.0 to 1.0")
    evidence: Optional[str] = Field(None, description="Verbatim text quote from the resume supporting this extraction")

class PersonalInformation(BaseModel):
    name: Optional[str] = Field(None, description="Candidate's full name")
    email: Optional[str] = Field(None, description="Contact email address")
    phone: Optional[str] = Field(None, description="Contact phone number")
    location: Optional[str] = Field(None, description="City, State, Country location")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    portfolio: Optional[str] = Field(None, description="Portfolio or personal website URL")

class CategorizedSkills(BaseModel):
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    libraries: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud: List[str] = Field(default_factory=list)
    ai_ml: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    other_skills: List[str] = Field(default_factory=list)

class WorkExperienceItem(BaseModel):
    company: str = Field(..., description="Employer / organization name")
    designation: str = Field(..., description="Role / Job title")
    start_date: Optional[str] = Field(None, description="Normalized start date (YYYY-MM or YYYY)")
    end_date: Optional[str] = Field(None, description="Normalized end date (YYYY-MM, YYYY, or Present)")
    is_current: bool = Field(False, description="Whether this is the candidate's active role")
    duration_months: int = Field(0, description="Calculated duration for this individual job")
    responsibilities: Optional[str] = Field(None, description="Responsibilities and achievements")

class EducationItem(BaseModel):
    institution: Optional[str] = Field(None, description="School, College, or University name")
    degree: Optional[str] = Field(None, description="Degree or diploma title (e.g. B.Tech, MS)")
    field: Optional[str] = Field(None, description="Field of study or specialization")
    start_year: Optional[str] = Field(None, description="Starting year (YYYY)")
    end_year: Optional[str] = Field(None, description="Graduation / completion year (YYYY)")

class ProjectItem(BaseModel):
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Summary of project and key contributions")
    technologies: Optional[str] = Field(None, description="Tech stack or languages used")
    link: Optional[str] = Field(None, description="Repository or live URL")

class CertificationItem(BaseModel):
    name: str = Field(..., description="Certification credential title")
    issuer: Optional[str] = Field(None, description="Issuing organization (e.g. AWS, Microsoft)")
    issue_date: Optional[str] = Field(None, description="Issue date or year")

class ParsedCandidateData(BaseModel):
    personal_information: PersonalInformation
    professional_summary: Optional[str] = Field(None, description="Executive summary or objective")
    skills: CategorizedSkills
    work_experience: List[WorkExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    total_experience_months: int = Field(0, description="Deterministic overlap-free career duration in months")
    total_experience_years: float = Field(0.0, description="Deterministic overlap-free career duration in years")
    confidence_and_evidence: Dict[str, FieldConfidenceEvidence] = Field(default_factory=dict)

class ParsingMetadata(BaseModel):
    engine: str = Field(..., description="Engine used (e.g. hybrid, spacy_rule, ollama)")
    duration_ms: float = Field(..., description="Processing duration in milliseconds")
    file_type: str = Field(..., description="File format (.pdf, .docx, etc.)")
    file_size_bytes: int = Field(..., description="Upload file size in bytes")

class ResumeParseResponse(BaseModel):
    status: str = Field("success", description="Status code string")
    data: ParsedCandidateData
    metadata: ParsingMetadata

class ForwardingResult(BaseModel):
    destination_url: str
    destination_status_code: int
    destination_response: Any
    forwarding_duration_ms: float
    masked_auth_header: Optional[str] = None

class ParseAndSendResponse(BaseModel):
    status: str = Field("success", description="'success' or 'forwarding_error'")
    parsed_resume: ParsedCandidateData
    forwarding: ForwardingResult
    metadata: ParsingMetadata

