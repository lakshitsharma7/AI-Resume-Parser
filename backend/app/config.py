import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
DATABASE_FILE = STORAGE_DIR / "resume_parser.db"

# Ensure directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    APP_NAME: str = "AI Resume Parser"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Storage & Database
    STORAGE_DIR: Path = STORAGE_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    DATABASE_URL: str = f"sqlite:///{DATABASE_FILE.as_posix()}"
    
    # Local AI Configuration (Ollama)
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "phi3:mini")
    OLLAMA_TIMEOUT: float = 25.0
    
    # OCR Configuration
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "")
    
    # Extraction Limits
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg"]
    STORE_UPLOADED_FILES_PERMANENTLY: bool = False

    # Forwarding / SSRF Protection Configuration
    FORWARD_REQUEST_TIMEOUT: float = 15.0
    ALLOW_LOCAL_DESTINATIONS: bool = os.getenv("ALLOW_LOCAL_DESTINATIONS", "false").lower() in ["true", "1", "yes"]

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
