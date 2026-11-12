# Testing Guide & Accuracy Benchmark (TESTING_GUIDE.md)

## System: AI-Powered Resume Parser (Standalone Application)
**Document Version:** 1.0.0  
**Testing Methodology:** Automated Unit Tests, Integration Tests, Ground-Truth Matrix Verification  

---

## 1. Testing Strategy

The evaluation protocol covers 8 standard resume archetypes representing real-world hiring variations:

| Archetype ID | Archetype Description | Key Challenges Evaluated |
|:---|:---|:---|
| **ARCH-1** | Simple One-Page Resume | Single-column, standard linear layout, clean headings. |
| **ARCH-2** | Two-Column Layout Resume | Left sidebar (Skills/Contact) + Right body (Experience/Education); multi-column spatial reading. |
| **ARCH-3** | Multi-Page Resume (3 Pages) | Page break bridging, continued experience bullet points across pages. |
| **ARCH-4** | Scanned / Image-Based PDF | Optical Character Recognition (OCR), degraded text reconstruction. |
| **ARCH-5** | Microsoft Word (.docx) | Native XML paragraph, run, and table extraction. |
| **ARCH-6** | Overlapping Employment Periods | Multiple companies with overlapping dates; non-inflated experience calculation. |
| **ARCH-7** | Incomplete / Sparse Data | Missing phone, missing degree, missing portfolio; verification that missing fields remain `null`. |
| **ARCH-8** | Tables & Complex Formatting | Bordered tables for skills/education, nested bullet points. |

---

## 2. Accuracy Evaluation Metric

Field-level extraction accuracy is measured against strict ground-truth annotations:

$$\text{Accuracy} = \frac{\text{True Positives}}{\text{Total Ground Truth Fields}} \times 100$$

### Target Metrics:
- **Contact Details (Email / Phone / URLs)**: >= 98% accuracy.
- **Skills Categorization**: >= 92% accuracy with zero false-positives for single-letter words (e.g., C/R/Go).
- **Date Overlap Calculations**: 100% mathematical precision (zero double-counting of simultaneous calendar months).
- **Grounding Compliance**: 100% (zero hallucinated company names or fictitious titles).

---

## 3. Running Automated Tests

Navigate to `backend/`:
```powershell
cd "d:\AI resume\AI-Resume-Parser\backend"
.\venv\Scripts\activate
```

### Run All Unit & Integration Tests:
```powershell
pytest -v
```

### Run Accuracy Benchmark Matrix:
```powershell
pytest tests/test_accuracy_matrix.py -v -s
```

### Run Specific Test Modules:
- **Text Extractor**: `pytest tests/test_extractor.py -v`
- **Timeline & Experience Math**: `pytest tests/test_timeline.py -v`
- **NLP & Regex Parser**: `pytest tests/test_nlp_parser.py -v`
- **End-to-End API**: `pytest tests/test_api.py -v`
