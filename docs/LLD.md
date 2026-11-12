# Low-Level Design (LLD.md)

## System: AI-Powered Resume Parser (Standalone Application)
**Document Version:** 1.0.0  
**Target:** Implementation Specifications, Classes, Algorithms, and Schema  

---

## 1. Class & Module Architecture

### 1.1 Text Extraction Service (`services/extractor.py`)

#### `DocumentExtractor`
- `extract(file_path: str) -> ExtractedDocument`
  - Detects extension (`.pdf`, `.docx`, `.doc`, `.png`, `.jpg`).
  - Calls sub-handlers:
    - `_extract_pdf(path: str) -> str`:
      - Opens document via `pdfplumber.open(path)`.
      - Inspects each page. Evaluates bounding box centroids (`x0`, `x1`).
      - If 2-column layout detected (median horizontal gap > threshold), sorts words within column 1 first, then column 2.
      - Falls back to `pypdf.PdfReader` if `pdfplumber` fails on corrupted streams.
      - If text is empty or shorter than 60 characters, invokes `_extract_ocr(path)`.
    - `_extract_docx(path: str) -> str`:
      - Uses `docx.Document(path)`.
      - Iterates over paragraphs, tables, and cell texts.
    - `_extract_ocr(path: str) -> str`:
      - Renders PDF page to image using `pypdf`/`PIL` and invokes `pytesseract.image_to_string`.
      - Gracefully catches `TesseractNotFoundError` and logs warning if binary is absent.

---

### 1.2 Deterministic & NLP Parser (`services/nlp_parser.py`)

#### `RegexRuleParser`
- **Email Extraction**:
  - Pattern: `r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'`
  - Validates TLD domain length >= 2, removes trailing punctuation.
- **Phone Extraction**:
  - Pattern: `r'(?:(?:\+|00)?\d{1,3}[-.\s]?)?(?:\(?\d{2,5}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{4,5}'`
  - Cleans whitespace and confirms total digit count between 10 and 15.
- **Links Extraction**:
  - Matches `linkedin.com/in/[a-zA-Z0-9_-]+`, `github.com/[a-zA-Z0-9_-]+`, and generic portfolio domains.
- **Section Segmentation**:
  - Scans for standard headers:
    - `SUMMARY`, `EXPERIENCE`, `WORK HISTORY`, `EMPLOYMENT`, `EDUCATION`, `SKILLS`, `PROJECTS`, `CERTIFICATIONS`, `ACHIEVEMENTS`.
  - Splits document into partitioned text windows.

#### `SkillDictionaryMatcher`
- Curated JSON taxonomy containing 800+ categorized tech skills:
  - `programming_languages`: Python, TypeScript, JavaScript, Java, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Dart, SQL, R, Scala.
  - `frameworks`: React, Next.js, FastAPI, Django, Flask, Express, Angular, Vue.js, Spring Boot, ASP.NET, Laravel.
  - `libraries`: NumPy, Pandas, Scikit-Learn, PyTorch, TensorFlow, Redux, Tailwind CSS, Bootstrap, jQuery, Celery.
  - `databases`: PostgreSQL, MySQL, SQLite, MongoDB, Redis, Elasticsearch, Oracle, Microsoft SQL Server, Cassandra, DynamoDB.
  - `cloud`: AWS, Azure, Google Cloud Platform (GCP), Docker, Kubernetes, Terraform, Cloudflare, Nginx, Linux.
  - `ai_ml`: LLMs, LangChain, LlamaIndex, Ollama, Machine Learning, Deep Learning, Computer Vision, NLP, HuggingFace.
  - `tools`: Git, GitHub, GitLab, Postman, JIRA, Docker, VS Code, Figma, Vite, Webpack, Jenkins.
- **Boundary Matching**: Uses word boundary `\b` regex checks to avoid false positives (e.g., matching "Go" inside "Google" or "C" inside "CSS").

---

### 1.3 Timeline & Overlap Calculator (`services/timeline.py`)

#### `ExperienceCalculator`
- **Problem**: When a candidate has overlapping jobs (e.g. Freelance 2021-01 to 2022-06, and Full-time 2021-06 to 2023-01), summing durations results in 18 + 19 = 37 months. The actual elapsed calendar period is 2021-01 to 2023-01 = 25 months.
- **Algorithm**:
  1. Parse `start_date` and `end_date` into `(year, month)`. For "Present" or "Current", use current year and month.
  2. Map each employment duration into a set of discrete `(year, month)` tuples or sort intervals `[start_month_index, end_month_index]`.
  3. Merge overlapping intervals:
     ```python
     intervals.sort(key=lambda x: x[0])
     merged = []
     for start, end in intervals:
         if not merged or merged[-1][1] < start:
             merged.append([start, end])
         else:
             merged[-1][1] = max(merged[-1][1], end)
     total_months = sum((end - start + 1) for start, end in merged)
     years = round(total_months / 12.0, 1)
     ```
  4. Returns: `total_experience_years` and individual duration for each job entry.

---

### 1.4 Ollama AI Client (`services/ollama_client.py`)

#### `OllamaClient`
- **Configuration**:
  - `OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")`
  - `OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")`
- **Methods**:
  - `is_available() -> bool`: Sends `GET /api/tags` with a 1.5s timeout.
  - `parse_resume_json(text: str) -> dict`:
    - Sends prompt instructing the model to extract JSON adhering to the strict schema.
    - Sets `options={"temperature": 0.0, "num_ctx": 4096}` for deterministic 8GB RAM safe execution.
    - Uses `format="json"` parameter native to Ollama.
    - Catches JSON decoding errors or timeouts and falls back to deterministic engine.

---

### 1.5 Confidence Scoring Engine (`services/confidence.py`)

- **Heuristic**:
  - `Email`: 1.0 if valid RFC regex match found; 0.0 if null.
  - `Phone`: 0.95 if formatted 10-15 digit string found; 0.0 if null.
  - `Name`: 0.90 if extracted from prominent top header and matched spaCy `PERSON`; 0.65 if extracted from heuristics; 0.0 if null.
  - `Experience Records`: 0.85 if company name, title, and valid dates all present; 0.50 if dates or company ambiguous.
  - `Skills`: 0.95 if exact dictionary match; 0.70 if inferred by LLM.

---

### 1.6 Excel & JSON Export Service (`services/export_service.py`)

- **JSON**: Formats candidate profile into complete clean JSON.
- **Excel (`openpyxl`)**:
  - Creates styled `.xlsx` workbook with primary brand palette (`#1E3A8A` dark blue header, white text, bordered data rows).
  - Sheet 1: `Candidate Overview` (Full Name, Contact, Social Links, Summary, Total Experience).
  - Sheet 2: `Employment History` (Company, Role, Start Date, End Date, Duration, Responsibilities).
  - Sheet 3: `Technical Skills` (Category, Skill Name, Normalized Name).
  - Sheet 4: `Education` (Degree, Institution, University, Specialization, Graduation Year).
  - Sheet 5: `Projects & Certifications`.
