# API Documentation (API_DOCUMENTATION.md)

## System: AI-Powered Resume Parser (Standalone Application)
**Base URL:** `http://localhost:8000/api/v1`  
**Protocol:** HTTP / JSON (REST)  
**Authentication:** Local Standalone Mode (None required for local single-user)  

---

## 1. Endpoints Overview

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/health` | Service health status and Ollama/OCR connectivity check |
| `POST` | `/resumes/upload` | Upload a resume (PDF/DOCX/image) and trigger automatic parsing |
| `GET` | `/resumes/` | List all parsed resumes with metadata |
| `GET` | `/resumes/{resume_id}` | Retrieve raw resume extraction metadata and status |
| `GET` | `/candidates/{candidate_id}` | Get full structured candidate profile |
| `PUT` | `/candidates/{candidate_id}` | Update candidate profile with user edits and corrections |
| `GET` | `/candidates/{candidate_id}/export/json` | Export candidate profile as `.json` file |
| `GET` | `/candidates/{candidate_id}/export/excel` | Export candidate profile as `.xlsx` multi-sheet Excel file |
| `DELETE`| `/resumes/{resume_id}` | Delete resume and associated candidate profile |

---

## 2. Detailed Endpoint Specifications

### 2.1 `GET /health`
Verifies backend operational status, database connectivity, Ollama server status, and Tesseract OCR availability.

#### Response (200 OK):
```json
{
  "status": "ok",
  "database": "connected",
  "ollama": {
    "available": true,
    "model": "phi3:mini",
    "host": "http://localhost:11434"
  },
  "tesseract_ocr": {
    "available": true
  },
  "version": "1.0.0"
}
```

---

### 2.2 `POST /resumes/upload`
Uploads resume file, extracts text, executes parsing pipeline, validates schema, and returns candidate profile.

#### Request:
- **Content-Type**: `multipart/form-data`
- **Body Parameter**: `file` (Binary: PDF, DOCX, PNG, JPG; max 25 MB)

#### Response (201 Created):
```json
{
  "status": "success",
  "resume_id": "c1f7a39e-2144-4822-b5e0-84cf04218a01",
  "candidate_id": "902d1843-1fb3-4f51-b841-862d64a4b111",
  "parsing_engine": "hybrid",
  "candidate": {
    "id": "902d1843-1fb3-4f51-b841-862d64a4b111",
    "personal_information": {
      "full_name": "Jane Doe",
      "email": "jane.doe@example.com",
      "phone": "+1-555-0199",
      "location": "San Francisco, CA",
      "linkedin": "https://linkedin.com/in/janedoe",
      "github": "https://github.com/janedoe",
      "portfolio": "https://janedoe.dev",
      "confidence": {
        "full_name": 0.95,
        "email": 1.0,
        "phone": 0.95,
        "location": 0.85,
        "linkedin": 1.0,
        "github": 1.0,
        "portfolio": 0.9
      }
    },
    "professional_information": {
      "summary": "Full Stack Engineer with 4.5 years of experience building scalable distributed web applications...",
      "total_experience_years": 4.5,
      "current_company": "Tech Solutions Inc.",
      "current_job_title": "Senior Software Engineer",
      "employment_history": [
        {
          "id": "emp_1",
          "company_name": "Tech Solutions Inc.",
          "job_title": "Senior Software Engineer",
          "start_date": "2022-03",
          "end_date": "Present",
          "is_current": true,
          "duration_months": 28,
          "responsibilities": "Architected microservices using FastAPI and React...",
          "confidence_score": 0.95
        }
      ]
    },
    "skills": {
      "programming_languages": ["Python", "TypeScript", "SQL"],
      "frameworks": ["FastAPI", "React", "Django"],
      "libraries": ["Pydantic", "Tailwind CSS"],
      "databases": ["PostgreSQL", "SQLite", "Redis"],
      "cloud": ["AWS", "Docker"],
      "ai_ml": ["Ollama", "spaCy"],
      "tools": ["Git", "GitHub", "VS Code"],
      "other_skills": ["RESTful APIs", "Agile / Scrum"]
    },
    "education": [
      {
        "id": "edu_1",
        "degree": "B.Tech in Computer Science",
        "institution": "University of California",
        "university": "UC Berkeley",
        "specialization": "Computer Science & Engineering",
        "graduation_year": "2020",
        "score": "3.8 GPA",
        "confidence_score": 0.92
      }
    ],
    "projects": [
      {
        "id": "proj_1",
        "title": "Cloud Resume Parser",
        "description": "Engineered offline resume extraction pipeline.",
        "technologies": "FastAPI, React, SQLite, Ollama",
        "link": "https://github.com/janedoe/parser",
        "confidence_score": 0.9
      }
    ],
    "certifications": [
      {
        "id": "cert_1",
        "name": "AWS Certified Solutions Architect",
        "issuer": "Amazon Web Services",
        "issue_date": "2023",
        "confidence_score": 0.95
      }
    ],
    "internships": [],
    "achievements": [],
    "languages": ["English", "Spanish"],
    "missing_fields": []
  }
}
```

---

### 2.3 `PUT /candidates/{candidate_id}`
Allows user/recruiter to update any field, edit employment records, add/remove skills, and correct missing information.

#### Request Body:
JSON matching candidate profile structure.

#### Response (200 OK):
Updated candidate JSON object.

---

### 2.4 `GET /candidates/{candidate_id}/export/excel`
Generates a multi-sheet formatted Excel workbook (`.xlsx`) using `openpyxl`.

#### Response:
- **Content-Type**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Content-Disposition**: `attachment; filename="Candidate_<name>_Profile.xlsx"`

