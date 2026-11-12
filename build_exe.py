import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
BACKEND_DIR = BASE_DIR / "backend"

print(f"Building Standalone Executable in: {BASE_DIR}")

# Verify frontend build exists
if not (FRONTEND_DIST / "index.html").exists():
    print("[!] Frontend dist not found. Building frontend first...")
    subprocess.run(["npm", "--prefix", str(BASE_DIR / "frontend"), "run", "build"], check=True)

pyinstaller_cmd = [
    sys.executable,
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    "--name", "AI-Resume-Parser",
    f"--paths={BACKEND_DIR}",
    f"--add-data={FRONTEND_DIST};frontend/dist",
    "--collect-data=en_core_web_sm",
    "--collect-data=spacy",
    "--copy-metadata=spacy",
    "--copy-metadata=en_core_web_sm",
    "--hidden-import=uvicorn.logging",
    "--hidden-import=uvicorn.loops",
    "--hidden-import=uvicorn.loops.auto",
    "--hidden-import=uvicorn.protocols",
    "--hidden-import=uvicorn.protocols.http",
    "--hidden-import=uvicorn.protocols.http.auto",
    "--hidden-import=uvicorn.lifespans",
    "--hidden-import=uvicorn.lifespans.on",
    "--hidden-import=en_core_web_sm",
    "--hidden-import=spacy.lang.en",
    "--hidden-import=pdfplumber",
    "--hidden-import=docx",
    "--hidden-import=openpyxl",
    "--hidden-import=sqlalchemy.dialects.sqlite",
    str(BASE_DIR / "desktop_runner.py")
]

print("Executing PyInstaller command...")
res = subprocess.run(pyinstaller_cmd, cwd=str(BASE_DIR))
if res.returncode == 0:
    print("\n[SUCCESS] Build complete! Executable located at: dist/AI-Resume-Parser.exe")
else:
    print(f"\n[ERROR] PyInstaller failed with exit code: {res.returncode}")
    sys.exit(res.returncode)

