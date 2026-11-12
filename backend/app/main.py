import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database import init_db, get_db
from app.routers import resumes, candidates
from app.schemas.candidate_schema import HealthResponse
from app.schemas.resume_parse_schema import ParsedCandidateData
from app.services.ollama_client import OllamaClient
from app.services.extractor import is_tesseract_available

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite database
    logger.info("Initializing SQLite database tables...")
    init_db()
    logger.info("Database initialized successfully.")
    yield
    # Shutdown
    logger.info("Application shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Standalone AI-Powered Resume Parser API (100% Free, Local, Offline-First)",
    lifespan=lifespan
)

# Enable CORS for local Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(resumes.router, prefix="/api/v1")
app.include_router(candidates.router, prefix="/api/v1")

@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Returns backend health status, database connection, Ollama availability, and Tesseract OCR status.
    """
    # Test DB connection
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    ollama_info = OllamaClient.check_availability()
    tesseract_info = {
        "available": is_tesseract_available(),
        "configured_cmd": settings.TESSERACT_CMD or "Default System PATH"
    }

    return HealthResponse(
        status="ok",
        database=db_status,
        ollama=ollama_info,
        tesseract_ocr=tesseract_info,
        version=settings.APP_VERSION
    )

@app.get("/api/v1/schema", tags=["Schema"])
def get_resume_schema():
    """
    Returns the supported JSON schema for parsed resume candidate profiles.
    Conforms to JSON Schema specification (Pydantic v2 / Draft 2020-12).
    """
    return ParsedCandidateData.model_json_schema()

from pathlib import Path
import sys
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Determine frontend static directory (supports both local repo and PyInstaller bundle)
def get_frontend_dist() -> Path | None:
    bundle_dir = getattr(sys, '_MEIPASS', None)
    if bundle_dir:
        cand = Path(bundle_dir) / "frontend" / "dist"
        if cand.exists():
            return cand
    cand = settings.BASE_DIR.parent / "frontend" / "dist"
    if cand.exists():
        return cand
    return None

frontend_dist = get_frontend_dist()
if frontend_dist and (frontend_dist / "index.html").exists():
    if (frontend_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/", tags=["UI"])
    def index():
        return FileResponse(str(frontend_dist / "index.html"))
else:
    @app.get("/", tags=["Root"])
    def root():
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs_url": "/docs",
            "health_url": "/api/v1/health",
            "schema_url": "/api/v1/schema"
        }

