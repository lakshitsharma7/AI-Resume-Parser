# AI-Powered Resume Parser (Standalone Application)

An offline-first, highly accurate, open-source AI Resume Parsing application designed to parse resumes in PDF, DOCX, and Scanned formats, extract candidate details into structured JSON, provide an editable candidate profile dashboard, and export to JSON and Excel.

Built with **FastAPI**, **React 18 + Vite**, **SQLite**, and **Ollama (Phi-3 Mini / Llama 3.2)**, featuring a zero-cloud, 100% free tech stack.

---

## 🌟 Key Highlights

- **100% Offline & Private**: Zero cloud API dependencies; candidate data never leaves your computer.
- **Strict Anti-Hallucination Grounding**: Never invents or assumes missing information; absent fields remain `null` and are clearly flagged.
- **Dual-Engine Architecture**: Combines local Ollama LLMs with deterministic spaCy & Regex NLP for speed, reliability, and precision.
- **Accurate Timeline Calculations**: Handles overlapping job periods and calculates actual elapsed career experience without double-counting.
- **Layout-Aware Extraction**: Column-aware PDF text extraction avoids interleaving two-column resumes.
- **Interactive Candidate Profile Dashboard**: Review, edit, and correct extracted information with real-time confidence scores before saving.
- **One-Click Exports**: Export candidate data to structured JSON and multi-sheet styled Excel (`.xlsx`) workbooks.
- **Completely Independent**: Zero coupling or connection with any external projects or databases.

---

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate      # Windows (or source venv/bin/activate on Linux/Mac)
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000
```
Backend Swagger API docs available at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend UI available at: `http://localhost:5173`

---

## 📖 Complete Documentation

| Document | Link / File | Description |
|:---|:---|:---|
| **High-Level Design** | [HLD.md](HLD.md) | Architectural tiers, data flow, and components |
| **Low-Level Design** | [LLD.md](LLD.md) | Class design, algorithms, regex patterns, schemas |
| **Requirements** | [REQUIREMENTS.md](REQUIREMENTS.md) | Functional, non-functional, and hardware specs |
| **Architecture** | [ARCHITECTURE.md](ARCHITECTURE.md) | Layered boundaries, licensing review, stack |
| **Database Design** | [DATABASE_DESIGN.md](DATABASE_DESIGN.md) | SQLite schema, ERD, and data dictionary |
| **API Documentation** | [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | REST endpoints, request/response payloads |
| **Project Structure** | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Directory layout and file responsibilities |
| **Installation Guide** | [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) | Setup instructions for Windows, Linux, Mac |
| **Testing Guide** | [TESTING_GUIDE.md](TESTING_GUIDE.md) | Benchmark matrix & accuracy validation |

---

## 🛠 Tech Stack

- **Backend**: FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0, SQLite
- **Text Extraction**: pdfplumber, pypdf, python-docx, pytesseract, Pillow
- **NLP & Parsing**: spaCy, Regex, Dateutil
- **Local AI**: Ollama (`phi3:mini`, `llama3.2:1b`, `llama3.2:3b`) with offline fallback
- **Exporting**: openpyxl (styled Excel), JSON
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React, Axios

---

## 🔒 License & Independence

This project is licensed under the MIT License. It is completely independent and contains zero proprietary or cloud-dependent code.
