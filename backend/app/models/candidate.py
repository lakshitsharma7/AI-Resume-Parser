import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=True)
    total_experience_years = Column(Float, default=0.0)
    summary = Column(Text, nullable=True)
    current_company = Column(String(200), nullable=True)
    current_job_title = Column(String(200), nullable=True)
    overall_confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="candidate")
    personal_info = relationship("PersonalInfo", back_populates="candidate", uselist=False, cascade="all, delete-orphan")
    employment_history = relationship("EmploymentHistory", back_populates="candidate", cascade="all, delete-orphan", order_by="EmploymentHistory.sort_order")
    skills = relationship("Skill", back_populates="candidate", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="candidate", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="candidate", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="candidate", cascade="all, delete-orphan")
    additional_info = relationship("AdditionalInfo", back_populates="candidate", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Candidate {self.id}>"


class PersonalInfo(Base):
    __tablename__ = "personal_info"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, unique=True)
    full_name = Column(String(150), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(200), nullable=True)
    linkedin = Column(String(300), nullable=True)
    github = Column(String(300), nullable=True)
    portfolio = Column(String(300), nullable=True)
    confidence_scores_json = Column(Text, nullable=True)  # JSON-encoded confidence per field

    candidate = relationship("Candidate", back_populates="personal_info")


class EmploymentHistory(Base):
    __tablename__ = "employment_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String(200), nullable=False)
    job_title = Column(String(200), nullable=False)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    is_current = Column(Boolean, default=False)
    duration_months = Column(Integer, default=0)
    responsibilities = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.85)
    sort_order = Column(Integer, default=0)

    candidate = relationship("Candidate", back_populates="employment_history")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)  # programming_languages, frameworks, databases, cloud, ai_ml, tools, other_skills
    skill_name = Column(String(100), nullable=False)
    normalized_name = Column(String(100), nullable=False)
    confidence_score = Column(Float, default=0.90)

    candidate = relationship("Candidate", back_populates="skills")


class Education(Base):
    __tablename__ = "education"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    degree = Column(String(150), nullable=True)
    institution = Column(String(250), nullable=True)
    university = Column(String(250), nullable=True)
    specialization = Column(String(150), nullable=True)
    graduation_year = Column(String(20), nullable=True)
    score = Column(String(50), nullable=True)
    confidence_score = Column(Float, default=0.85)

    candidate = relationship("Candidate", back_populates="education")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    technologies = Column(String(300), nullable=True)
    link = Column(String(300), nullable=True)
    confidence_score = Column(Float, default=0.85)

    candidate = relationship("Candidate", back_populates="projects")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    issuer = Column(String(200), nullable=True)
    issue_date = Column(String(50), nullable=True)
    confidence_score = Column(Float, default=0.90)

    candidate = relationship("Candidate", back_populates="certifications")


class AdditionalInfo(Base):
    __tablename__ = "additional_info"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    info_type = Column(String(50), nullable=False)  # "internship", "achievement", "language"
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="additional_info")

