# Project Structure (PROJECT_STRUCTURE.md)

## System: AI-Powered Resume Parser (Standalone Application)
**Root Directory:** `d:\AI resume\AI-Resume-Parser`  

---

```
AI-Resume-Parser/
├── docs/                             # Architecture & Project Documentation
│   ├── HLD.md                        # High-Level Design
│   ├── LLD.md                        # Low-Level Design
│   ├── REQUIREMENTS.md               # Functional & Non-Functional Requirements
│   ├── ARCHITECTURE.md               # System Architecture & Component Mapping
│   ├── DATABASE_DESIGN.md            # ERD & Table Schemas
│   ├── API_DOCUMENTATION.md          # REST API Specification
│   ├── PROJECT_STRUCTURE.md          # Repository & Directory Blueprint
│   ├── INSTALLATION_GUIDE.md         # Setup and Startup Instructions
│   ├── TESTING_GUIDE.md              # Test Strategy & Accuracy Verification
│   └── README.md                     # Overview & Quickstart Guide
│
├── backend/                          # FastAPI Backend Application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI Application Entrypoint
│   │   ├── config.py                 # App Settings & Environment Variables
│   │   ├── database.py               # SQLite Engine & Session Local
│   │   ├── models/                   # SQLAlchemy ORM Models
│   │   │   ├── __init__.py
│   │   │   ├── resume.py             # Resume & Extraction Log Model
│   │   │   └── candidate.py          # Candidate & Associated Relational Models
│   │   ├── schemas/                  # Pydantic v2 Validation Schemas
│   │   │   ├── __init__.py
│   │   │   └── candidate_schema.py   # Candidate, Employment, Skill, Education Schemas
│   │   ├── services/                 # Core Business Logic & AI Engines
│   │   │   ├── __init__.py
│   │   │   ├── extractor.py          # PDF / DOCX / OCR Text Extraction
│   │   │   ├── nlp_parser.py         # Regex + spaCy Deterministic Parser
│   │   │   ├── ollama_client.py      # Ollama HTTP Client (phi3:mini / llama3.2)
│   │   │   ├── timeline.py           # Overlap-Free Date Arithmetic
│   │   │   ├── skill_taxonomy.py     # 800+ Categorized Skills Dictionary
│   │   │   ├── merger.py             # Pipeline Fusion & Grounding Logic
│   │   │   └── export_service.py     # openpyxl Multi-Sheet Excel & JSON Export
│   │   └── routers/                  # API Endpoint Controllers
│   │       ├── __init__.py
│   │       ├── resumes.py            # Upload & Extraction Endpoints
│   │       └── candidates.py         # Candidate Profile CRUD & Exports
│   │
│   ├── storage/                      # Isolated Local Storage
│   │   ├── uploads/                  # Uploaded Resume Documents (.pdf, .docx)
│   │   └── resume_parser.db          # Isolated SQLite Database
│   │
│   ├── tests/                        # Backend Test Suite
│   │   ├── __init__.py
│   │   ├── test_extractor.py         # Tests for PDF, DOCX, and OCR
│   │   ├── test_nlp_parser.py        # Tests for Regex, spaCy, and Skills
│   │   ├── test_timeline.py          # Overlapping Dates & Experience Math
│   │   ├── test_api.py               # End-to-End FastAPI Tests
│   │   └── test_accuracy_matrix.py   # Benchmark Against 8 Standard Resume Archetypes
│   │
│   ├── requirements.txt              # Backend Dependencies (Python)
│   └── run.bat                       # Windows 1-Click Backend Launch Script
│
├── frontend/                         # React 18 + Vite Frontend Application
│   ├── public/                       # Static Assets & Icons
│   ├── src/
│   │   ├── assets/
│   │   ├── components/               # UI Modular Components
│   │   │   ├── Navbar.tsx            # Header & System Status Indicator
│   │   │   ├── UploadZone.tsx        # Drag & Drop File Upload with Progress
│   │   │   ├── CandidateProfile.tsx  # Interactive Editable Profile Container
│   │   │   ├── PersonalInfoCard.tsx  # Personal Details & Confidence Display
│   │   │   ├── ExperienceTimeline.tsx# Employment History with Overlap Badges
│   │   │   ├── SkillsManager.tsx     # Categorized Skills Badges & Editing
│   │   │   ├── EducationSection.tsx  # Education & Academic Details
│   │   │   ├── ProjectsSection.tsx   # Projects & Portfolio Links
│   │   │   ├── CertificationsList.tsx# Certifications & Badges
│   │   │   ├── MissingFieldAlert.tsx # Warning Banner for Missing Fields
│   │   │   └── CandidateListModal.tsx# Previously Parsed Resumes Drawer
│   │   ├── services/
│   │   │   └── api.ts                # Axios API Client
│   │   ├── types/
│   │   │   └── candidate.ts          # TypeScript Types & Interfaces
│   │   ├── App.tsx                   # Main Application Layout
│   │   ├── index.css                 # Tailwind CSS Directives
│   │   └── main.tsx                  # React DOM Entrypoint
│   │
│   ├── index.html
│   ├── package.json                  # Frontend Dependencies (Node.js)
│   ├── tsconfig.json                 # TypeScript Configuration
│   ├── vite.config.ts                # Vite Configuration
│   └── tailwind.config.js            # Tailwind Styling Configuration
│
├── test_resumes/                     # Evaluation Resumes (All 8 Archetypes)
│   ├── 01_simple_one_page.pdf
│   ├── 02_two_column_layout.pdf
│   ├── 03_multipage_resume.pdf
│   ├── 04_scanned_image_resume.pdf
│   ├── 05_standard_word.docx
│   ├── 06_overlapping_companies.pdf
│   ├── 07_incomplete_data.pdf
│   └── 08_tables_and_formatting.pdf
│
└── README.md                         # Quickstart & System Documentation
```

