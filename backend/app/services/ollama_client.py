import json
import logging
import httpx
from typing import Optional, Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert, strict AI resume extraction engine.
Your task is to extract candidate information from the provided resume text into valid JSON.

CRITICAL RULES:
1. ONLY extract information that is explicitly stated in the resume text.
2. NEVER invent, assume, or hallucinate missing information.
3. If a field is not present in the resume, return null.
4. Categorize skills accurately into the specified categories.
5. Identify employment history with exact company names, job titles, start dates, and end dates.
6. Return ONLY a valid JSON object matching the requested schema. No markdown formatting, no conversational text.
"""

JSON_SCHEMA_EXAMPLE = {
    "personal_information": {
        "full_name": None,
        "email": None,
        "phone": None,
        "location": None,
        "linkedin": None,
        "github": None,
        "portfolio": None
    },
    "professional_information": {
        "summary": None,
        "current_company": None,
        "current_job_title": None,
        "employment_history": [
            {
                "company_name": "Company",
                "job_title": "Title",
                "start_date": "YYYY-MM",
                "end_date": "YYYY-MM or Present",
                "is_current": True,
                "responsibilities": "Job duties and achievements"
            }
        ]
    },
    "skills": {
        "programming_languages": [],
        "frameworks": [],
        "libraries": [],
        "databases": [],
        "cloud": [],
        "ai_ml": [],
        "tools": [],
        "other_skills": []
    },
    "education": [
        {
            "degree": "Degree Name",
            "institution": "Institution Name",
            "university": "University",
            "specialization": "Specialization",
            "graduation_year": "YYYY",
            "score": "GPA or Score"
        }
    ],
    "projects": [
        {
            "title": "Project Name",
            "description": "Project Description",
            "technologies": "Technologies Used",
            "link": "Project URL"
        }
    ],
    "certifications": [
        {
            "name": "Certification Title",
            "issuer": "Issuer",
            "issue_date": "YYYY"
        }
    ],
    "languages": []
}

class OllamaClient:
    """
    Client for local AI processing via Ollama.
    Supports lightweight models (Phi-3 Mini, Llama 3.2, Qwen 2.5).
    Gracefully falls back if Ollama is offline or model is missing.
    """

    @classmethod
    def check_availability(cls) -> Dict[str, Any]:
        """Checks if Ollama service is reachable and lists available models."""
        import socket
        from urllib.parse import urlparse

        parsed_url = urlparse(settings.OLLAMA_HOST)
        host = parsed_url.hostname or "127.0.0.1"
        port = parsed_url.port or 11434

        # Ultra-fast socket pre-check (2ms) to avoid blocking thread when Ollama is offline
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            result = sock.connect_ex((host, port))
            sock.close()
            if result != 0:
                return {
                    "available": False,
                    "host": settings.OLLAMA_HOST,
                    "configured_model": settings.OLLAMA_MODEL,
                    "model_ready": False,
                    "installed_models": []
                }
        except Exception:
            return {
                "available": False,
                "host": settings.OLLAMA_HOST,
                "configured_model": settings.OLLAMA_MODEL,
                "model_ready": False,
                "installed_models": []
            }

        try:
            with httpx.Client(timeout=1.5) as client:
                res = client.get(f"{settings.OLLAMA_HOST}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    preferred = settings.OLLAMA_MODEL
                    has_model = any(preferred in m for m in models)
                    return {
                        "available": True,
                        "host": settings.OLLAMA_HOST,
                        "configured_model": preferred,
                        "model_ready": has_model,
                        "installed_models": models
                    }
        except Exception:
            pass

        return {
            "available": False,
            "host": settings.OLLAMA_HOST,
            "configured_model": settings.OLLAMA_MODEL,
            "model_ready": False,
            "installed_models": []
        }

    @classmethod
    def extract_with_llm(cls, text: str) -> Optional[Dict[str, Any]]:
        """
        Sends resume text to local Ollama LLM with strict JSON schema.
        Returns parsed dictionary or None if Ollama fails or times out.
        """
        status = cls.check_availability()
        if not status["available"]:
            logger.info("Ollama is not running. Using deterministic NLP engine.")
            return None

        # Truncate text if excessively long to safeguard 8 GB RAM usage
        max_chars = 12000
        truncated_text = text[:max_chars]

        prompt = f"""Extract all candidate details from the following resume text into JSON format.

JSON Schema format:
{json.dumps(JSON_SCHEMA_EXAMPLE, indent=2)}

Resume Text:
\"\"\"
{truncated_text}
\"\"\"

Remember: Return ONLY the JSON object. Do NOT invent missing values."""

        try:
            with httpx.Client(timeout=settings.OLLAMA_TIMEOUT) as client:
                payload = {
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "system": SYSTEM_PROMPT,
                    "format": "json",
                    "stream": False,
                    "options": {
                        "temperature": 0.0,
                        "num_ctx": 4096
                    }
                }
                response = client.post(f"{settings.OLLAMA_HOST}/api/generate", json=payload)
                if response.status_code == 200:
                    result = response.json()
                    raw_content = result.get("response", "").strip()
                    parsed = json.loads(raw_content)
                    return parsed
        except Exception as e:
            logger.warning(f"Ollama inference error or timeout: {e}. Falling back to rule-based engine.")

        return None
