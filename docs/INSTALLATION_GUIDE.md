# Installation & Setup Guide (INSTALLATION_GUIDE.md)

## System: AI-Powered Resume Parser (Standalone Application)
**Document Version:** 1.0.0  
**Target Environment:** Windows 10/11 (Compatible with Linux / macOS)  

---

## 1. Prerequisites

Before installing the application, ensure the following are installed on your machine:
- **Python**: Version 3.10, 3.11, or 3.12 (Verify with `python --version`).
- **Node.js**: Version 18.x or 20.x+ with `npm` (Verify with `node --version`).
- **Git**: (Optional, for tracking).

### Optional (For Enhanced AI & OCR):
- **Ollama**: Free local LLM runner ([Download Ollama for Windows](https://ollama.com/download)).
  - Pull a lightweight model (ideal for 8 GB RAM laptops):
    ```bash
    ollama pull phi3:mini
    # OR
    ollama pull llama3.2:1b
    # OR
    ollama pull llama3.2:3b
    ```
  - *Note: If Ollama is not installed or running, the application automatically uses its built-in rule-based + spaCy NLP extraction engine without crashing or blocking.*
- **Tesseract OCR**: Free local OCR engine ([UB-Mannheim Tesseract Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki)).
  - Install and add to system PATH (e.g. `C:\Program Files\Tesseract-OCR`).
  - *Note: If Tesseract is not installed, native text extraction works for all regular PDF and DOCX files.*

---

## 2. Step-by-Step Installation

### Step 2.1: Clone / Navigate to Project Directory
```powershell
cd "d:\AI resume\AI-Resume-Parser"
```

### Step 2.2: Backend Setup
1. Create a Python virtual environment:
   ```powershell
   cd backend
   python -m venv venv
   ```
2. Activate the virtual environment:
   ```powershell
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # OR Windows Command Prompt:
   .\venv\Scripts\activate.bat
   ```
3. Install Python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Download the lightweight spaCy English model:
   ```powershell
   python -m spacy download en_core_web_sm
   ```

### Step 2.3: Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```powershell
   cd "d:\AI resume\AI-Resume-Parser\frontend"
   ```
2. Install dependencies:
   ```powershell
   npm install
   ```

---

## 3. Running the Application

### Option A: 1-Click Launchers
- **Backend**: Double-click or run `backend/run.bat` (starts FastAPI at `http://localhost:8000`).
- **Frontend**: In the frontend directory, run `npm run dev` (starts Vite at `http://localhost:5173`).

### Option B: Manual Command Line
1. **Start Backend Server**:
   ```powershell
   cd "d:\AI resume\AI-Resume-Parser\backend"
   .\venv\Scripts\activate
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   The backend API docs (Swagger UI) will be available at:
   `http://127.0.0.1:8000/docs`

2. **Start Frontend Server**:
   ```powershell
   cd "d:\AI resume\AI-Resume-Parser\frontend"
   npm run dev
   ```
   Open your browser and visit:
   `http://localhost:5173`

---

## 4. Verification & Health Check

Visit `http://localhost:8000/api/v1/health` in your browser. You should see:
```json
{
  "status": "ok",
  "database": "connected",
  "ollama": { "available": true, "model": "phi3:mini" },
  "tesseract_ocr": { "available": true },
  "version": "1.0.0"
}
```
If Ollama or Tesseract are not yet running, the status will show `"available": false` with an advisory note, and the system will smoothly fall back to high-accuracy deterministic extraction.
