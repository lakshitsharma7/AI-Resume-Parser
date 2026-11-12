export interface PersonalInfo {
  full_name: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
  linkedin: string | null;
  github: string | null;
  portfolio: string | null;
  confidence?: Record<string, number>;
}

export interface EmploymentHistoryItem {
  id?: string;
  company_name: string;
  job_title: string;
  start_date: string | null;
  end_date: string | null;
  is_current: boolean;
  duration_months: number;
  responsibilities: string | null;
  confidence_score: number;
}

export interface ProfessionalInfo {
  summary: string | null;
  total_experience_years: number;
  current_company: string | null;
  current_job_title: string | null;
  employment_history: EmploymentHistoryItem[];
}

export interface CategorizedSkills {
  programming_languages: string[];
  frameworks: string[];
  libraries: string[];
  databases: string[];
  cloud: string[];
  ai_ml: string[];
  tools: string[];
  other_skills: string[];
}

export interface EducationItem {
  id?: string;
  degree: string | null;
  institution: string | null;
  university: string | null;
  specialization: string | null;
  graduation_year: string | null;
  score: string | null;
  confidence_score: number;
}

export interface ProjectItem {
  id?: string;
  title: string;
  description: string | null;
  technologies: string | null;
  link: string | null;
  confidence_score: number;
}

export interface CertificationItem {
  id?: string;
  name: string;
  issuer: string | null;
  issue_date: string | null;
  confidence_score: number;
}

export interface CandidateProfile {
  id: string;
  resume_id: string;
  personal_information: PersonalInfo;
  professional_information: ProfessionalInfo;
  skills: CategorizedSkills;
  education: EducationItem[];
  projects: ProjectItem[];
  certifications: CertificationItem[];
  internships: Array<{ id?: string; title: string; description?: string }>;
  achievements: string[];
  languages: string[];
  missing_fields: string[];
  overall_confidence: number;
  created_at?: string;
  updated_at?: string;
}

export interface HealthStatus {
  status: string;
  database: string;
  ollama: {
    available: boolean;
    host: string;
    configured_model: string;
    model_ready: boolean;
    installed_models: string[];
  };
  tesseract_ocr: {
    available: boolean;
    configured_cmd: string;
  };
  version: string;
}

export interface CandidateSummary {
  id: string;
  resume_id: string;
  full_name: string | null;
  email: string | null;
  phone: string | null;
  current_job_title: string | null;
  current_company: string | null;
  total_experience_years: number;
  overall_confidence: number;
  created_at: string | null;
}

