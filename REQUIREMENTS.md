# Requirements Specification (REQUIREMENTS.md)

## Project: AI-Powered Resume Parser (Standalone Application)
**Version:** 1.0.0  
**Environment:** Local, 100% Free & Open-Source, Zero Cloud Dependencies  
**Author:** AI Resume Parser Team  

---

## 1. Executive Summary & Objective

The **AI-Powered Resume Parser** is an independent, offline-first application designed to ingest resumes in multiple formats (PDF, DOCX, Scanned Images), accurately extract candidate information using a combination of local lightweight LLMs (via Ollama) and deterministic NLP/Regex parsing engines, validate and ground the data with confidence scoring, and present an interactive, editable candidate profile dashboard with one-click JSON and Excel exports.

### Core Tenet
- **Zero Cloud Dependence**: 100% local processing; candidate resumes and PII never leave the host machine.
- **Strict Grounding**: Zero hallucination; missing information is preserved as `null` with explicit visual warnings.
- **Project Independence**: Absolute isolation from any third-party or legacy projects, external databases, or proprietary APIs.

---

## 2. Functional Requirements

### FR-1: File Ingestion & Format Support
- **FR-1.1**: Support native PDF files (single-page, multi-page, multi-column, and table-based).
- **FR-1.2**: Support Microsoft Word DOCX files (standard paragraphs, tables, header/footer).
- **FR-1.3**: Support Scanned and Image-based PDFs via Tesseract OCR fallback.
- **FR-1.4**: Validate file format, file size limits (up to 25 MB), and prevent malicious file uploads.

### FR-2: Information Extraction Scope
The parser must extract and categorize:
1. **Personal Information**:
   - `full_name`: Candidate's legal or professional name.
   - `email`: Validated email address.
   - `phone`: Local or international formatted telephone number.
   - `location`: City, State, and Country.
   - `linkedin`: LinkedIn profile URL or handle.
   - `github`: GitHub profile URL or handle.
   - `portfolio`: Personal website or portfolio URL.
2. **Professional Summary & Experience**:
   - `summary`: High-level executive summary / objective statement.
   - `current_job_title`: Active or most recent title.
   - `current_company`: Active or most recent employer.
   - `total_experience_years`: Overlap-free calculated duration across all jobs.
   - `employment_history`: Array of records containing:
     - `company_name`: Official employer name.
     - `job_title`: Designation / Role.
     - `start_date`: In standard `YYYY-MM` or `YYYY` format.
     - `end_date`: `YYYY-MM`, `YYYY`, or `Present`.
     - `is_current`: Boolean flag.
     - `responsibilities`: List or structured text of key achievements/duties.
3. **Technical Skills Taxonomy**:
   - Structured categorization into:
     - `programming_languages` (e.g., Python, TypeScript, Java, C++)
     - `frameworks` (e.g., FastAPI, React, Django, Spring Boot)
     - `libraries` (e.g., NumPy, Pandas, Scikit-learn, Redux)
     - `databases` (e.g., PostgreSQL, SQLite, MongoDB, Redis)
     - `cloud` (e.g., AWS, Azure, GCP, Docker, Kubernetes)
     - `ai_ml` (e.g., PyTorch, TensorFlow, LangChain, Ollama, NLP)
     - `tools` (e.g., Git, JIRA, VS Code, Postman, Linux)
     - `other_skills` (Domain knowledge, Agile, CI/CD, etc.)
   - Preservation of original verbatim mentions alongside normalized names.
4. **Education**:
   - Array of records with `degree`, `institution`/`college`, `university`, `specialization`, `graduation_year`, `score`/`gpa`.
5. **Additional Details**:
   - `projects`: Project title, description, technologies used, URL.
   - `certifications`: Certification title, issuing authority, issue date.
   - `internships`: Practical training and internship positions.
   - `achievements`: Awards, honors, hackathons, publications.
   - `languages`: Spoken and written natural languages with proficiency.

### FR-3: Extraction Accuracy & Rules
- **FR-3.1 Grounding**: Never fabricate or assume information. If absent, set field to `null`.
- **FR-3.2 Date Overlap Handling**: Calculate non-overlapping working periods to prevent inflated experience counts (e.g., concurrent freelance or dual roles).
- **FR-3.3 Confidence Indicators**: Assign confidence levels (`high`: >0.85, `medium`: 0.60–0.85, `low`: <0.60) per primary field.
- **FR-3.4 Multi-Column Preservation**: Use spatial text extraction (`pdfplumber` bounding-box column sorting) to avoid interleaving disparate text blocks.

### FR-4: User Interface & Experience
- **FR-4.1 Upload & Progress**: Drag-and-drop file upload with visual extraction stages (Upload → Read → NLP/AI → Complete).
- **FR-4.2 Candidate Profile Dashboard**: Segmented views for Personal, Experience, Skills, Education, Projects, and Certifications.
- **FR-4.3 Inline Editing**: Allow recruiters/users to modify, add, or delete any extracted field before committing to database.
- **FR-4.4 Missing Information Flags**: Prominently tag missing essential fields (`Email Missing`, `Phone Unverified`, etc.).
- **FR-4.5 Export Capabilities**:
  - Download full parsed profile as structured JSON (`.json`).
  - Download comprehensive multi-sheet Excel workbook (`.xlsx`) generated via `openpyxl`.

### FR-5: Standalone Database Persistence
- **FR-5.1**: Persist all uploaded resumes and parsed candidate records into an isolated SQLite database (`resume_parser.db`).
- **FR-5.2**: Provide CRUD APIs to view past parsed resumes and candidate profiles.

---

## 3. Non-Functional Requirements

| Requirement | Metric / Specification |
|:---|:---|
| **Memory Footprint** | Peak RAM <= 2.5 GB (Backend + Frontend + NLP). Compatible with 8 GB RAM laptops. |
| **Parsing Latency** | Heuristic/spaCy engine: < 2.5 seconds. Ollama hybrid inference: < 15 seconds. |
| **Availability / Offline** | 100% operational offline without internet connection. |
| **Portability** | Cross-platform (Windows 10/11, Linux, macOS). |
| **Licensing** | Permissive open-source only (MIT, Apache 2.0, BSD). PyMuPDF (AGPL) is strictly excluded. |

---

## 4. Hardware & Operating Constraints
- **Host OS**: Windows (tested on Windows 11/10).
- **CPU**: x86_64 / Intel or AMD with AVX2 support.
- **RAM**: 8 GB host RAM budget.
- **Local AI Model**: Quantized Phi-3 Mini (3.8B 4-bit) or Llama 3.2 (1B/3B 4-bit) via Ollama, with automated rule-based fallback when Ollama is inactive.

