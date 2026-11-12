import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_RESUME_DOC = """
David Miller
Seattle, WA | david.miller@example.com | +1 206-555-0144
https://linkedin.com/in/davidmiller | https://github.com/davidmiller

PROFESSIONAL SUMMARY
Backend Engineer with 3 years of experience developing microservices in Python and Go.

EXPERIENCE
Software Engineer | CloudScale Inc | 2021-06 to Present
- Developed REST APIs in FastAPI and Go.
- Implemented PostgreSQL database schemas and Redis caching.

Junior Developer | DevStudio | 2020-01 to 2021-05
- Built web interfaces with React and TypeScript.

EDUCATION
Bachelor of Science in Computer Science | 2016 - 2020
University of Washington

SKILLS
Python, Go, TypeScript, FastAPI, React, PostgreSQL, Docker, Git

PROJECTS
CacheProxy | Go, Redis | https://github.com/davidmiller/cacheproxy
High-performance in-memory caching proxy.

CERTIFICATIONS
Docker Certified Associate (2022)
"""

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert "ollama" in data

def test_upload_resume_and_parse():
    # Create fake text file as a doc or simulate upload
    file_bytes = SAMPLE_RESUME_DOC.encode("utf-8")
    
    # We can test with a text/docx/pdf file or test the parser directly
    # For multipart upload endpoint, let's create a minimal PDF or DOCX using python-docx
    import docx
    doc = docx.Document()
    for line in SAMPLE_RESUME_DOC.strip().split("\n"):
        doc.add_paragraph(line)
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    
    response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("david_miller.docx", bio, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["candidate"] is not None
    assert data["candidate"]["personal_information"]["email"] == "david.miller@example.com"
    assert data["candidate"]["personal_information"]["full_name"] == "David Miller"
    
    candidate_id = data["candidate_id"]
    resume_id = data["resume_id"]
    
    # Test candidate retrieval
    res_get = client.get(f"/api/v1/candidates/{candidate_id}")
    assert res_get.status_code == 200
    cand = res_get.json()
    assert cand["personal_information"]["email"] == "david.miller@example.com"
    
    # Test candidate update (editing profile)
    update_payload = {
        "personal_information": {
            "full_name": "David Miller, Lead",
            "location": "Seattle, Washington, USA"
        }
    }
    res_put = client.put(f"/api/v1/candidates/{candidate_id}", json=update_payload)
    assert res_put.status_code == 200
    updated_cand = res_put.json()
    assert updated_cand["personal_information"]["full_name"] == "David Miller, Lead"
    assert updated_cand["personal_information"]["location"] == "Seattle, Washington, USA"
    
    # Test JSON export
    res_json_exp = client.get(f"/api/v1/candidates/{candidate_id}/export/json")
    assert res_json_exp.status_code == 200
    assert "David Miller" in res_json_exp.text
    
    # Test Excel export
    res_xl_exp = client.get(f"/api/v1/candidates/{candidate_id}/export/excel")
    assert res_xl_exp.status_code == 200
    assert res_xl_exp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(res_xl_exp.content) > 1000  # Valid Excel file bytes

