# Architecture Specification (ARCHITECTURE.md)

## System: AI-Powered Resume Parser (Standalone Application)
**Document Version:** 1.0.0  
**Design Philosophy:** Modular, 100% Local, Decoupled Frontend/Backend  

---

## 1. System Context & Boundary

The system operates strictly within the host machine boundaries:

```
+-----------------------------------------------------------------------------------+
| Host Machine (Windows 10/11 / Linux / macOS)                                      |
|                                                                                   |
|  [ Browser Client ]                                                               |
|         |                                                                         |
|         v (HTTP / localhost:5173 -> localhost:8000)                                |
|  +-----------------------------------------------------------------------------+  |
|  | AI-Resume-Parser Backend (FastAPI / Python 3.12)                            |  |
|  |                                                                             |  |
|  |  +-------------------+   +--------------------+   +-----------------------+ |  |
|  |  |  Document Reader  |-->| Text Normalizer &  |-->| Parsing Pipeline      | |  |
|  |  |  (pdfplumber,     |   | Column Sorter      |   | (Dual: Rule + Ollama) | |  |
|  |  |   python-docx,    |   +--------------------+   +-----------------------+ |  |
|  |  |   Tesseract OCR)  |                                        |             |  |
|  |  +-------------------+                                        v             |  |
|  |                                                   +-----------------------+ |  |
|  |                                                   | Validation & Scorer   | |  |
|  |                                                   | (Pydantic v2)         | |  |
|  |                                                   +-----------------------+ |  |
|  |                                                               |             |  |
|  |  +-------------------+                                        v             |  |
|  |  | Export Engine     |<-------------------------- [ SQLite Database ]       |  |
|  |  | (openpyxl / JSON) |                            (resume_parser.db)        |  |
|  |  +-------------------+                                                      |  |
|  +-----------------------------------------------------------------------------+  |
|         |                                                                         |
|         v (Optional Local Loopback HTTP)                                          |
|  [ Ollama Service (localhost:11434 / phi3:mini or llama3.2) ]                     |
+-----------------------------------------------------------------------------------+
```

---

## 2. Layered Architecture

### Layer 1: Presentation (React + Vite)
- **Directory**: `frontend/`
- **Key Modules**:
  - `src/components/UploadZone.tsx`: File upload area with drag & drop, file type verification, progress bar.
  - `src/components/CandidateProfile.tsx`: The primary dashboard with tabbed layout.
  - `src/components/ConfidenceBadge.tsx`: Visual chip rendering High/Medium/Low confidence scores.
  - `src/components/MissingFieldAlert.tsx`: Notice cards highlighting missing information.
  - `src/components/CandidateHistory.tsx`: List of previously parsed resumes with search and quick actions.
  - `src/services/api.ts`: Typed Axios/Fetch client interacting with the FastAPI backend.

### Layer 2: API Gateway & Application Layer (FastAPI)
- **Directory**: `backend/app/`
- **Modules**:
  - `main.py`: Application entrypoint, CORS configuration, exception handlers.
  - `routers/resumes.py`: Endpoints for uploading, parsing, candidate retrieval, updates, and exports.
  - `models/`: SQLAlchemy database models.
  - `schemas/`: Pydantic validation schemas.
  - `services/`: Business logic, document reading, NLP parsing, Ollama bridging, timeline arithmetic, and Excel exporting.

### Layer 3: Persistence Layer (SQLite)
- Standalone file: `backend/storage/resume_parser.db`.
- No external DB server required. Auto-initialized on first run.

---

## 3. Technology Stack & Licensing Review

| Technology | License | Commercial Compatibility | Purpose |
|:---|:---|:---|:---|
| **FastAPI** | MIT | Permissive / Free | High-performance Python async REST API |
| **Uvicorn** | BSD-3-Clause | Permissive / Free | ASGI web server |
| **Pydantic v2** | MIT | Permissive / Free | Schema validation & serialization |
| **SQLAlchemy 2** | MIT | Permissive / Free | Database ORM |
| **pdfplumber** | MIT | Permissive / Free | Layout & column-aware PDF text extraction |
| **pypdf** | BSD-3-Clause | Permissive / Free | PDF stream fallback |
| **python-docx** | MIT | Permissive / Free | DOCX extraction |
| **pytesseract** | Apache 2.0 | Permissive / Free | Scanned PDF / image OCR wrapper |
| **spaCy** | MIT | Permissive / Free | NLP tokenization and Named Entity Recognition |
| **openpyxl** | MIT | Permissive / Free | Styled Excel (`.xlsx`) generation |
| **React 18** | MIT | Permissive / Free | Frontend UI framework |
| **Vite** | MIT | Permissive / Free | Fast modern frontend bundler |
| **Tailwind CSS**| MIT | Permissive / Free | Utility-first responsive styling |
| **Lucide Icons**| ISC | Permissive / Free | UI iconography |
| **Ollama** | MIT | Permissive / Free | Local lightweight LLM execution |
| **Phi-3 Mini** | MIT | Permissive / Free | 3.8B quantized local inference |

> **Note on PyMuPDF**: Excluded intentionally per user requirements to avoid AGPL licensing obligations.

