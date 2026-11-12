import io
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock
import pytest
from fastapi.testclient import TestClient
import httpx

from app.main import app

client = TestClient(app)
TEST_RESUMES_DIR = Path(__file__).resolve().parent.parent.parent / "test_resumes"

# -----------------------------------------------------------------------------
# 1. Health and Schema Endpoints
# -----------------------------------------------------------------------------

def test_health_check_endpoint():
    """Verify GET /api/v1/health returns 200 with engine statuses."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert "ollama" in data
    assert "tesseract_ocr" in data
    assert "version" in data


def test_schema_endpoint():
    """Verify GET /api/v1/schema returns valid JSON Schema for candidate profile."""
    response = client.get("/api/v1/schema")
    assert response.status_code == 200
    schema = response.json()
    assert schema.get("title") == "ParsedCandidateData"
    assert "properties" in schema
    props = schema["properties"]
    assert "personal_information" in props
    assert "professional_summary" in props
    assert "skills" in props
    assert "work_experience" in props
    assert "education" in props
    assert "projects" in props
    assert "certifications" in props
    assert "languages" in props
    assert "total_experience_months" in props
    assert "total_experience_years" in props
    assert "confidence_and_evidence" in props


# -----------------------------------------------------------------------------
# 2. POST /api/v1/resumes/parse Endpoint
# -----------------------------------------------------------------------------

def test_parse_pdf_resume():
    """Verify parsing a standard PDF resume returns structured validated JSON."""
    pdf_path = TEST_RESUMES_DIR / "01_simple_one_page.pdf"
    assert pdf_path.exists(), f"Missing fixture {pdf_path}"

    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/v1/resumes/parse",
            files={"file": ("01_simple_one_page.pdf", f, "application/pdf")}
        )

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["status"] == "success"

    data = res_json["data"]
    personal = data["personal_information"]
    assert "Alex" in (personal["name"] or "")
    assert personal["email"] == "alex.mercer@example.com"
    assert personal["phone"] is not None

    # Verify work experience
    assert len(data["work_experience"]) >= 1
    assert data["total_experience_months"] > 0
    assert data["total_experience_years"] > 0.0

    # Verify confidence and evidence
    assert "confidence_and_evidence" in data
    assert isinstance(data["confidence_and_evidence"], dict)

    # Verify metadata
    metadata = res_json["metadata"]
    assert metadata["file_type"] == ".pdf"
    assert metadata["duration_ms"] > 0


def test_parse_docx_resume():
    """Verify parsing a DOCX resume returns structured JSON with skills & experience."""
    docx_path = TEST_RESUMES_DIR / "05_standard_word.docx"
    assert docx_path.exists(), f"Missing fixture {docx_path}"

    with open(docx_path, "rb") as f:
        response = client.post(
            "/api/v1/resumes/parse",
            files={"file": ("05_standard_word.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["status"] == "success"
    data = res_json["data"]
    assert data["personal_information"]["email"] == "rachel.adams@example.com"
    assert len(data["work_experience"]) >= 1
    assert res_json["metadata"]["file_type"] == ".docx"


def test_parse_overlapping_dates_handling():
    """Verify overlapping employment intervals are not double counted."""
    overlap_pdf = TEST_RESUMES_DIR / "06_overlapping_companies.pdf"
    assert overlap_pdf.exists(), f"Missing fixture {overlap_pdf}"

    with open(overlap_pdf, "rb") as f:
        response = client.post(
            "/api/v1/resumes/parse",
            files={"file": ("06_overlapping_companies.pdf", f, "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()["data"]
    # Total experience should be exactly the non-overlapping union (30 months: Jan 2020 - Jun 2022)
    # rather than summing 30 + 18 = 48 months.
    assert data["total_experience_months"] == 30


# -----------------------------------------------------------------------------
# 3. POST /api/v1/resumes/parse-and-send Endpoint
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_parse_and_send_success():
    """
    Verify POST /api/v1/resumes/parse-and-send parses resume, forwards JSON
    to destination API, masks sensitive auth tokens, and preserves response.
    """
    pdf_path = TEST_RESUMES_DIR / "01_simple_one_page.pdf"

    mock_resp = httpx.Response(
        status_code=201,
        json={"ats_candidate_id": "ATS-9988", "status": "created", "accepted": True},
        request=httpx.Request("POST", "https://api.external-ats.com/v1/candidates")
    )

    with patch("app.services.forwarder.validate_destination_url", return_value=(True, "")), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp) as mock_post:
        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/v1/resumes/parse-and-send",
                files={"file": ("01_simple_one_page.pdf", f, "application/pdf")},
                data={
                    "destination_url": "https://api.external-ats.com/v1/candidates",
                    "auth_token": "secret_super_confidential_token_xyz123",
                    "auth_header_name": "Authorization",
                    "auth_scheme": "Bearer",
                    "custom_headers": json.dumps({"X-Client-ID": "PartnerApp42"})
                }
            )

        assert response.status_code == 200
        res_json = response.json()
        assert res_json["status"] == "success"

        # Check candidate data
        parsed = res_json["parsed_resume"]
        assert parsed["personal_information"]["email"] == "alex.mercer@example.com"

        # Check forwarding results
        forwarding = res_json["forwarding"]
        assert forwarding["destination_url"] == "https://api.external-ats.com/v1/candidates"
        assert forwarding["destination_status_code"] == 201
        assert forwarding["destination_response"] == {"ats_candidate_id": "ATS-9988", "status": "created", "accepted": True}

        # CRITICAL SECURITY CHECK: Raw auth token must NEVER be exposed in response
        assert "secret_super_confidential_token_xyz123" not in response.text
        assert forwarding["masked_auth_header"] == "Bearer ****"

        # Verify mock was called with valid JSON payload and correct headers
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"]["personal_information"]["email"] == "alex.mercer@example.com"
        assert call_kwargs["headers"]["Authorization"] == "Bearer secret_super_confidential_token_xyz123"
        assert call_kwargs["headers"]["X-Client-ID"] == "PartnerApp42"
        assert call_kwargs["headers"]["Content-Type"] == "application/json"


# -----------------------------------------------------------------------------
# 4. SSRF Attack Prevention Tests
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("blocked_url", [
    "http://127.0.0.1:8000/webhook",
    "http://localhost:5000/api",
    "http://169.254.169.254/latest/meta-data",
    "http://192.168.1.1/admin",
    "http://10.0.0.5/api/v1/receive",
    "http://172.16.0.1/dump",
    "ftp://example.com/upload",
    "file:///etc/passwd"
])
def test_ssrf_blocked_destinations(blocked_url):
    """
    Verify destinations targeting local, private, metadata, or non-HTTP schemes
    are strictly rejected with status 403 without sending any outgoing request.
    """
    pdf_path = TEST_RESUMES_DIR / "01_simple_one_page.pdf"

    with patch("httpx.AsyncClient.post") as mock_post:
        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/v1/resumes/parse-and-send",
                files={"file": ("01_simple_one_page.pdf", f, "application/pdf")},
                data={"destination_url": blocked_url}
            )

        assert response.status_code == 200
        res_json = response.json()
        assert res_json["status"] == "forwarding_error"
        assert res_json["forwarding"]["destination_status_code"] == 403
        assert res_json["forwarding"]["destination_response"]["error"] == "SSRF_PROTECTION_BLOCKED"

        # Ensure no network socket request was dispatched
        mock_post.assert_not_called()


# -----------------------------------------------------------------------------
# 5. Gateway Timeout and Error Handling Tests
# -----------------------------------------------------------------------------

def test_destination_timeout_handling():
    """Verify that destination API timeout returns 504 Gateway Timeout in forwarding details."""
    pdf_path = TEST_RESUMES_DIR / "01_simple_one_page.pdf"

    with patch("app.services.forwarder.validate_destination_url", return_value=(True, "")), \
         patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Connection timed out")):
        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/v1/resumes/parse-and-send",
                files={"file": ("01_simple_one_page.pdf", f, "application/pdf")},
                data={"destination_url": "https://api.external-ats.com/v1/slow-endpoint"}
            )

        assert response.status_code == 200
        res_json = response.json()
        assert res_json["status"] == "forwarding_error"
        assert res_json["forwarding"]["destination_status_code"] == 504
        assert res_json["forwarding"]["destination_response"]["error"] == "GATEWAY_TIMEOUT"


def test_destination_connection_error_handling():
    """Verify that unreachable destination returns 502 Bad Gateway in forwarding details."""
    pdf_path = TEST_RESUMES_DIR / "01_simple_one_page.pdf"

    req = httpx.Request("POST", "https://api.external-ats.com/v1/down")
    with patch("app.services.forwarder.validate_destination_url", return_value=(True, "")), \
         patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Failed to establish connection", request=req)):
        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/v1/resumes/parse-and-send",
                files={"file": ("01_simple_one_page.pdf", f, "application/pdf")},
                data={"destination_url": "https://api.external-ats.com/v1/down"}
            )

        assert response.status_code == 200
        res_json = response.json()
        assert res_json["status"] == "forwarding_error"
        assert res_json["forwarding"]["destination_status_code"] == 502
        assert res_json["forwarding"]["destination_response"]["error"] == "BAD_GATEWAY"


# -----------------------------------------------------------------------------
# 6. File Upload Validation & Edge Cases
# -----------------------------------------------------------------------------

def test_empty_file_rejected():
    """Verify empty 0-byte file upload returns 400 Bad Request."""
    empty_bio = io.BytesIO(b"")
    response = client.post(
        "/api/v1/resumes/parse",
        files={"file": ("empty_resume.pdf", empty_bio, "application/pdf")}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_unsupported_file_extension_rejected():
    """Verify file with unsupported extension (e.g. .exe) returns 400 Bad Request."""
    fake_bio = io.BytesIO(b"Not an executable")
    response = client.post(
        "/api/v1/resumes/parse",
        files={"file": ("malicious.exe", fake_bio, "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()

